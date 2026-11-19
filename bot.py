import os
import time
import threading
import logging
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "9049655726:AAGhdmogKzkYOsyzJs-cv-6mtP7pY0PVtWA")
CHANNEL_ID = os.getenv("CHANNEL_ID", "-1004478174913")
WEB_PORT = int(os.getenv("PORT", "10000"))

state = {
    "market": "30S",
    "period": "00660",
    "action": "SMALL",
    "color": "GREEN",
    "color_emoji": "🟢",
    "number": "1",
    "waiting_for_period": False,
}


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"SIDDIK VIP BOT IS RUNNING")

    def log_message(self, format, *args):
        return


def start_web_server() -> None:
    server = HTTPServer(("0.0.0.0", WEB_PORT), HealthHandler)
    logger.info("HTTP health server listening on port %s", WEB_PORT)
    server.serve_forever()


def get_countdown_seconds(market: str) -> int:
    bd_time = datetime.now(timezone(timedelta(hours=6)))
    total_sec = int(bd_time.timestamp())
    return (30 - (total_sec % 30)) if market == "30S" else (60 - (total_sec % 60))


def format_period_last5(raw: str) -> str:
    cleaned = "".join(ch for ch in str(raw).strip() if ch.isalnum())
    if not cleaned:
        return "00000"
    return cleaned[-5:].zfill(5)


def build_signal_text() -> str:
    wingo_time = "𝟯𝟬𝗦" if state["market"] == "30S" else "𝟲𝟬𝗦"
    sec_left = get_countdown_seconds(state["market"])
    period_5 = format_period_last5(state["period"])

    return (
        "👑 SIDDIK VIP SIGNAL 👑\n"
        "▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"💎 𝐏𝐄𝐑𝐈𝐎𝐃 ➤ 📅 ...{period_5}\n"
        f"🎯 𝐀𝐂𝐓𝐈𝐎𝐍 ➤ BET {state['action']}\n"
        f"🎨 𝐂𝐎𝐋𝐎𝐑 ➤ {state['color_emoji']} {state['color']}\n"
        f"🔢 𝐍𝐔𝐌𝐁𝐄𝐑 ➤ 💠 [ {state['number']} ]\n"
        f"⚡ 𝐖𝐈𝐍𝐆𝐎 ➤ {wingo_time} ⏱️ ({sec_left}s)\n"
        "▱▱▱▱▱▱▱▱▱▱▱▱▱▱"
    )


def build_control_keyboard() -> InlineKeyboardMarkup:
    m_30 = "✅ WinGo 30S" if state["market"] == "30S" else "WinGo 30S"
    m_1m = "✅ WinGo 1M" if state["market"] == "1M" else "WinGo 1M"

    a_small = "✅ SMALL" if state["action"] == "SMALL" else "SMALL"
    a_big = "✅ BIG" if state["action"] == "BIG" else "BIG"

    c_green = "✅ 🟢 GREEN" if state["color"] == "GREEN" else "🟢 GREEN"
    c_red = "✅ 🔴 RED" if state["color"] == "RED" else "🔴 RED"
    c_violet = "✅ 🟣 VIOLET" if state["color"] == "VIOLET" else "🟣 VIOLET"

    num_row_1 = [
        InlineKeyboardButton(
            f"[{n}]" if state["number"] == n else f"{n}",
            callback_data=f"num_{n}",
        )
        for n in ["0", "1", "2", "3", "4"]
    ]
    num_row_2 = [
        InlineKeyboardButton(
            f"[{n}]" if state["number"] == n else f"{n}",
            callback_data=f"num_{n}",
        )
        for n in ["5", "6", "7", "8", "9"]
    ]

    keyboard = [
        [
            InlineKeyboardButton(m_30, callback_data="mkt_30S"),
            InlineKeyboardButton(m_1m, callback_data="mkt_1M"),
        ],
        [
            InlineKeyboardButton("✏️ Set Period", callback_data="set_period"),
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh_panel"),
        ],
        [
            InlineKeyboardButton(a_small, callback_data="act_SMALL"),
            InlineKeyboardButton(a_big, callback_data="act_BIG"),
        ],
        [
            InlineKeyboardButton(c_green, callback_data="col_GREEN"),
            InlineKeyboardButton(c_red, callback_data="col_RED"),
            InlineKeyboardButton(c_violet, callback_data="col_VIOLET"),
        ],
        num_row_1,
        num_row_2,
        [
            InlineKeyboardButton("🚀 Send to Channel", callback_data="send_signal"),
        ],
        [
            InlineKeyboardButton("💎 Win", callback_data="stk_💎 Win"),
            InlineKeyboardButton("🔥 Boom Shot", callback_data="stk_🔥 Boom Shot"),
            InlineKeyboardButton("❌ Loss", callback_data="stk_❌ Loss"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def send_to_telegram_channel(text: str) -> tuple[bool, str]:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(
            url,
            json={"chat_id": CHANNEL_ID, "text": text},
            timeout=15,
        )
        data = resp.json()
        if data.get("ok"):
            return True, "✅ চ্যানেলে পাঠানো হয়েছে!"
        return False, f"❌ এরর: {data.get('description', 'Unknown error')}"
    except Exception as exc:
        return False, f"❌ নেটওয়ার্ক সমস্যা: {exc}"


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state["waiting_for_period"] = False
    preview = build_signal_text()
    await update.message.reply_text(
        f"📋 **লাইভ প্রিভিউ:**\n\n{preview}",
        reply_markup=build_control_keyboard(),
        parse_mode="Markdown",
    )


async def period_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        state["waiting_for_period"] = True
        await update.message.reply_text("🎯 পিরিয়ড নাম্বার (বা শেষ ৫ ডিজিট) লিখে পাঠান:")
        return

    state["period"] = format_period_last5(" ".join(context.args))
    state["waiting_for_period"] = False
    await update.message.reply_text(
        f"✅ পিরিয়ড সেট হয়েছে: `...{state['period']}`\n\n{build_signal_text()}",
        reply_markup=build_control_keyboard(),
        parse_mode="Markdown",
    )


async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = (update.message.text or "").strip()
    if state["waiting_for_period"]:
        state["period"] = format_period_last5(msg)
        state["waiting_for_period"] = False
        await update.message.reply_text(
            f"✅ পিরিয়ড আপডেট হয়েছে: `...{state['period']}`\n\n{build_signal_text()}",
            reply_markup=build_control_keyboard(),
            parse_mode="Markdown",
        )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("mkt_"):
        state["market"] = data.split("_", 1)[1]
    elif data.startswith("act_"):
        state["action"] = data.split("_", 1)[1]
    elif data.startswith("col_"):
        col = data.split("_", 1)[1]
        state["color"] = col
        state["color_emoji"] = {"GREEN": "🟢", "RED": "🔴", "VIOLET": "🟣"}[col]
    elif data.startswith("num_"):
        state["number"] = data.split("_", 1)[1]
    elif data == "set_period":
        state["waiting_for_period"] = True
        await query.message.reply_text("🎯 পিরিয়ড নাম্বার লিখে পাঠান (যেমন `0660` বা পুরো নাম্বার):")
        return
    elif data == "send_signal":
        _, status_msg = send_to_telegram_channel(build_signal_text())
        await query.message.reply_text(status_msg)
        return
    elif data.startswith("stk_"):
        sticker_text = data.split("_", 1)[1]
        _, status_msg = send_to_telegram_channel(sticker_text)
        await query.message.reply_text(f"{sticker_text} — {status_msg}")
        return

    try:
        await query.edit_message_text(
            f"📋 **লাইভ প্রিভিউ:**\n\n{build_signal_text()}",
            reply_markup=build_control_keyboard(),
            parse_mode="Markdown",
        )
    except Exception:
        pass


def run_bot_forever() -> None:
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()

    while True:
        try:
            app = ApplicationBuilder().token(BOT_TOKEN).build()
            app.add_handler(CommandHandler("start", start_cmd))
            app.add_handler(CommandHandler("period", period_cmd))
            app.add_handler(CallbackQueryHandler(button_callback))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))

            logger.info("Starting Telegram bot polling...")
            app.run_polling(drop_pending_updates=True)
        except Exception as exc:
            logger.error("Bot crashed with error: %s. Restarting in 5 seconds...", exc)
            time.sleep(5)


if __name__ == "__main__":
    run_bot_forever()
