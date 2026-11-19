import logging
from datetime import datetime, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("JoyWingoBot")

TOKEN = "9064976363:AAF5y_IVLOQYFCkbsEGlKKR8ae3zKxu6Hsk"
CHANNEL_USERNAME = "@bdincomesitehgnice"
CHANNEL_URL = "https://t.me/bdincomesitehgnice"


def generate_html_style_period() -> tuple[str, int]:
    """
    HTML কোডের মতো UTC সময় অনুযায়ী 30s পিরিয়ড নাম্বার ও বাকি সেকেন্ড বের করে।
    """
    now = datetime.now(timezone.utc)
    duration = 30
    total_seconds_today = now.hour * 3600 + now.minute * 60 + now.second
    elapsed_in_period = total_seconds_today % duration
    period_index_today = (total_seconds_today // duration) + 1

    date_str = now.strftime("%Y%m%d")
    formatted_index = str(50000 + period_index_today).zfill(5)
    full_period = f"{date_str}1000{formatted_index}"
    time_left = duration - elapsed_in_period
    return full_period, time_left


def generate_signal_from_period(full_period: str) -> tuple[str, str, int]:
    """
    HTML কোডের লজিক অনুযায়ী পিরিয়ড থেকে BIG/SMALL, কালার ও নাম্বার তৈরি করে।
    """
    seed_val = int(full_period[-5:]) if full_period[-5:].isdigit() else 12345
    period_slot = int(datetime.now(timezone.utc).timestamp()) // 30
    market_flow_trend = (seed_val * 31 + period_slot) % 100

    is_big = market_flow_trend >= 46
    pred_type = "BIG" if is_big else "SMALL"
    action_text = f"BET {pred_type}"

    if is_big:
        lucky_num = 5 + ((seed_val + period_slot) % 5)
    else:
        lucky_num = (seed_val + period_slot) % 5

    if lucky_num in (0, 5):
        color_text = "🟣 VIOLET"
    elif lucky_num in (1, 3, 7, 9):
        color_text = "🟢 GREEN"
    else:
        color_text = "🔴 RED"

    return action_text, color_text, lucky_num


def format_signal_card(user_name: str) -> str:
    full_period, time_left = generate_html_style_period()
    action_text, color_text, lucky_num = generate_signal_from_period(full_period)

    return (
        f"👑 **OWNER OF JOY — VIP SIGNAL** 👑\n"
        f"👤 *User:* `{user_name}`\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"💎 **𝐏𝐄𝐑𝐈𝐎𝐃** ➤ 📅 `{full_period}`\n"
        f"⏳ **𝐓𝐈𝐌𝐄 𝐋𝐄𝐅𝐓** ➤ `{time_left:02d}s`\n"
        f"🎯 **𝐀𝐂𝐓𝐈𝐎𝐍** ➤ **{action_text}**\n"
        f"🎨 **𝐂𝐎𝐋𝐎𝐑** ➤ {color_text}\n"
        f"🔢 **𝐍𝐔𝐌𝐁𝐄𝐑** ➤ 💠  {lucky_num}\n"
        f"⚡ **𝐖𝐈𝐍𝐆𝐎** ➤ 𝟯𝟬𝗦 ⏱️\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱"
    )


async def is_user_joined(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ("member", "administrator", "creator", "restricted")
    except Exception as e:
        logger.warning(f"Channel membership check failed for {user_id}: {e}")
        return False


def get_join_verify_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 টেলিগ্রাম চ্যানেল জয়েন", url=CHANNEL_URL)],
        [InlineKeyboardButton("✅ জয়েন ভেরিফাই করুন", callback_data="verify_join")],
    ])


def get_signal_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 নতুন সিগন্যাল", callback_data="refresh_signal")]
    ])


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.message:
        return

    joined = await is_user_joined(user.id, context)
    if not joined:
        await update.message.reply_text(
            "🔒 **সিগন্যাল পেতে হলে আগে আমাদের টেলিগ্রাম চ্যানেলে জয়েন করতে হবে!**\n\n"
            "নিচের বাটনে ক্লিক করে চ্যানেলে জয়েন করুন, তারপর **✅ জয়েন ভেরিফাই করুন** চাপুন।",
            parse_mode="Markdown",
            reply_markup=get_join_verify_keyboard(),
        )
        return

    await update.message.reply_text(
        format_signal_card(user.first_name),
        parse_mode="Markdown",
        reply_markup=get_signal_keyboard(),
    )


async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.message:
        return

    joined = await is_user_joined(user.id, context)
    if not joined:
        await update.message.reply_text(
            "🔒 **আগে টেলিগ্রাম চ্যানেলে জয়েন করুন!**\n\n"
            "জয়েন করার পর **✅ জয়েন ভেরিফাই করুন** বাটনে চাপ দিন।",
            parse_mode="Markdown",
            reply_markup=get_join_verify_keyboard(),
        )
        return

    await update.message.reply_text(
        format_signal_card(user.first_name),
        parse_mode="Markdown",
        reply_markup=get_signal_keyboard(),
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return

    user = query.from_user
    if query.data == "verify_join":
        joined = await is_user_joined(user.id, context)
        if joined:
            await query.answer("ভেরিফাই সফল হয়েছে! ✅", show_alert=False)
            await query.edit_message_text(
                text=format_signal_card(user.first_name),
                parse_mode="Markdown",
                reply_markup=get_signal_keyboard(),
            )
        else:
            await query.answer("আপনি এখনো চ্যানেলে জয়েন করেননি! আগে জয়েন করুন।", show_alert=True)

    elif query.data == "refresh_signal":
        joined = await is_user_joined(user.id, context)
        if not joined:
            await query.answer("আগে চ্যানেলে জয়েন করুন!", show_alert=True)
            await query.edit_message_text(
                text="🔒 **আপনি চ্যানেল থেকে লিভ নিয়েছেন বা জয়েন করেননি। আগে জয়েন করুন!**",
                parse_mode="Markdown",
                reply_markup=get_join_verify_keyboard(),
            )
            return

        await query.answer("নতুন সিগন্যাল আপডেট হয়েছে! 🔄", show_alert=False)
        await query.edit_message_text(
            text=format_signal_card(user.first_name),
            parse_mode="Markdown",
            reply_markup=get_signal_keyboard(),
        )


def main() -> None:
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("signal", signal_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    logger.info("Bot started...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
