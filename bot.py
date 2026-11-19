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
logger = logging.getLogger("JoyWingoVIPBot")

TOKEN = "9064976363:AAF5y_IVLOQYFCkbsEGlKKR8ae3zKxu6Hsk"
CHANNEL_ID = "@bdincomesitehgnice"
CHANNEL_URL = "https://t.me/bdincomesitehgnice"
OWNER_USERNAME = "@BDT588"
OWNER_CONTACT_URL = "https://t.me/BDT588"

# মার্কেট কনফিগারেশন: key -> (display_label, duration_seconds, base_offset)
MARKETS: dict[str, tuple[str, int, int]] = {
    "30S": ("30S (৩০ সেকেন্ড)", 30, 50000),
    "1M": ("1M (১ মিনিট)", 60, 20000),
    "3M": ("3M (৩ মিনিট)", 180, 10000),
    "5M": ("5M (৫ মিনিট)", 300, 5000),
}

# ইউজার স্টেট ট্র্যাক করার ডিকশনারি
user_states: dict[int, dict[str, object]] = {}


def generate_market_period(market_key: str) -> tuple[str, int]:
    _, duration, base_offset = MARKETS[market_key]
    now = datetime.now(timezone.utc)
    total_seconds_today = now.hour * 3600 + now.minute * 60 + now.second
    elapsed_in_period = total_seconds_today % duration
    period_index_today = (total_seconds_today // duration) + 1

    date_str = now.strftime("%Y%m%d")
    formatted_index = str(base_offset + period_index_today).zfill(5)
    full_period = f"{date_str}1000{formatted_index}"
    time_left = duration - elapsed_in_period
    return full_period, time_left


def evaluate_actual_outcome(full_period: str) -> tuple[str, int]:
    actual_seed = int(full_period[-5:]) if full_period[-5:].isdigit() else 54321
    actual_num = (actual_seed * 13 + 7) % 10
    actual_size = "BIG" if actual_num >= 5 else "SMALL"
    return actual_size, actual_num


def generate_signal_for_market(market_key: str, full_period: str) -> tuple[str, str, str, int]:
    _, duration, _ = MARKETS[market_key]
    seed_val = int(full_period[-5:]) if full_period[-5:].isdigit() else 12345
    slot = int(datetime.now(timezone.utc).timestamp()) // duration
    market_flow_trend = (seed_val * 31 + slot) % 100

    is_big = market_flow_trend >= 46
    pred_type = "BIG" if is_big else "SMALL"
    action_text = f"BET {pred_type}"

    if is_big:
        lucky_num = 5 + ((seed_val + slot) % 5)
    else:
        lucky_num = (seed_val + slot) % 5

    if lucky_num in (0, 5):
        color_text = "🟣 VIOLET"
    elif lucky_num in (1, 3, 7, 9):
        color_text = "🟢 GREEN"
    else:
        color_text = "🔴 RED"

    return pred_type, action_text, color_text, lucky_num


def format_result_announcement(
    user_name: str,
    market_key: str,
    finished_period: str,
    predicted_type: str,
) -> str:
    market_label, _, _ = MARKETS[market_key]
    actual_size, actual_num = evaluate_actual_outcome(finished_period)
    is_win = predicted_type == actual_size

    if is_win:
        return (
            f"🏆 **CONGRATULATIONS! WIN!** 🎉\n"
            f"👑 **OWNER OF JOY — জয় (JOY)** 👑\n"
            f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
            f"👤 *Trader:* `{user_name}`\n"
            f"📊 **𝐌𝐀𝐑𝐊𝐄𝐓** ➤ **{market_label}**\n"
            f"💎 **𝐏𝐄𝐑𝐈𝐎𝐃** ➤ `{finished_period}`\n"
            f"🎯 **𝐀𝐂𝐓𝐈𝐎𝐍** ➤ **BET {predicted_type}**\n"
            f"🎲 **𝐑𝐄𝐒𝐔𝐋𝐓** ➤ **{actual_size}** (`#{actual_num}`)\n"
            f"✅ **𝐒𝐓𝐀𝐓𝐔𝐒** ➤ **উইন হয়েছে, কনগ্রাচুলেশনস! 🥳**\n"
            f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
            f"🌟 *জয় (JOY)-এর পক্ষ থেকে আন্তরিক অভিনন্দন!*\n"
            f"🚀 *নতুন সিগন্যাল নিচে দেওয়া হলো 👇*"
        )

    return (
        f"📌 **ROUND RESULT UPDATE** 📌\n"
        f"👑 **OWNER OF JOY — জয় (JOY)** 👑\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"👤 *Trader:* `{user_name}`\n"
        f"📊 **𝐌𝐀𝐑𝐊𝐄𝐓** ➤ **{market_label}**\n"
        f"💎 **𝐏𝐄𝐑𝐈𝐎𝐃** ➤ `{finished_period}`\n"
        f"🎯 **𝐀𝐂𝐓𝐈𝐎𝐍** ➤ **BET {predicted_type}**\n"
        f"🎲 **𝐑𝐄𝐒𝐔𝐋𝐓** ➤ **{actual_size}** (`#{actual_num}`)\n"
        f"❌ **𝐒𝐓𝐀𝐓𝐔𝐒** ➤ **LOSS (পরের রাউন্ডে ধৈর্য ধরে এগিয়ে যান)**\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"💡 *জয় (JOY)-এর বার্তা: ধৈর্য ও শৃঙ্খলাই আসল শক্তি।*\n"
        f"🚀 *নতুন সিগন্যাল নিচে দেওয়া হলো 👇*"
    )


def format_market_signal_card(
    user_name: str,
    market_key: str,
    period: str,
    time_left: int,
    auto_on: bool,
) -> tuple[str, str]:
    market_label, _, _ = MARKETS[market_key]
    pred_type, action_text, color_text, lucky_num = generate_signal_for_market(market_key, period)
    auto_status = "ON (Auto)" if auto_on else "OFF"

    card = (
        f"👑 **OWNER OF JOY — জয় (JOY)** 👑\n"
        f"👤 *Trader:* `{user_name}`\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"📊 **𝐌𝐀𝐑𝐊𝐄𝐓** ➤ **{market_label}**\n"
        f"💎 **𝐏𝐄𝐑𝐈𝐎𝐃** ➤ 📅 `{period}`\n"
        f"⏳ **𝐓𝐈𝐌𝐄 𝐋𝐄𝐅𝐓** ➤ `{time_left:02d}s`\n"
        f"🎯 **𝐀𝐂𝐓𝐈𝐎𝐍** ➤ **{action_text}**\n"
        f"🎨 **𝐂𝐎𝐋𝐎𝐑** ➤ {color_text}\n"
        f"🔢 **𝐍𝐔𝐌𝐁𝐄𝐑** ➤ 💠  {lucky_num}\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"🤖 *Auto Signal:* `{auto_status}`\n"
        f"✨ *Guided by:* **জয় (JOY)** | *Contact:* {OWNER_USERNAME}\n"
        f"💡 *পরামর্শ: আবেগ নয়, ধৈর্য ও মানি ম্যানেজমেন্ট মেনে চলুন।*"
    )
    return card, pred_type


def build_joy_about_message() -> str:
    return (
        f"👑 **OWNER OF JOY — জয় (JOY)** 👑\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"🌟 **পরিচালনায়:** **জয় (JOY)**\n"
        f"📲 **সরাসরি যোগাযোগ:** {OWNER_USERNAME}\n\n"
        f"💎 **জয় (JOY) সম্পর্কে কিছু কথা:**\n"
        f"**জয় (JOY)** একজন পরিশ্রমী, দূরদর্শী ও দায়িত্বশীল মানুষ, যিনি সবসময় ইউজারদের সঠিক দিকনির্দেশনা, "
        f"গোছানো সিস্টেম এবং আন্তরিক সহযোগিতা দেওয়ার চেষ্টা করেন। কঠিন সময়েও মাথা ঠান্ডা রেখে কীভাবে "
        f"সঠিক সিদ্ধান্ত নিতে হয় এবং নিজের লক্ষ্য ঠিক রাখতে হয়—এই মানসিকতাই **জয়**-কে আলাদা করে তোলে।\n\n"
        f"📖 **শিক্ষামূলক ও মোটিভেশনাল বার্তা:**\n"
        f"• *সফলতা কখনো ভাগ্যের ওপর ছেড়ে দেওয়ার বিষয় নয়; এটি তৈরি হয় ধৈর্য, নিয়মানুবর্তিতা এবং সঠিক পরিকল্পনার মাধ্যমে।*\n"
        f"• *প্রতিটি জয় থেকে বিনয়ী থাকুন, আর প্রতিটি ভুল থেকে শিখে আরও শক্তিশালী হয়ে উঠুন।*\n"
        f"• *নিজের সীমা ও বাজেট বুঝে চলুন—আত্মনিয়ন্ত্রণই একজন স্মার্ট মানুষের সবচেয়ে বড় সম্পদ।*\n\n"
        f"📞 **যেকোনো সমস্যা বা পরামর্শের জন্য যোগাযোগ করুন:** {OWNER_USERNAME}"
    )


async def is_user_joined(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        status = getattr(member, "status", "")
        return status in ("member", "administrator", "creator", "restricted")
    except Exception as e:
        logger.error(f"Membership check error for {user_id}: {e}")
        return False


def get_join_verify_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 টেলিগ্রাম চ্যানেল জয়েন", url=CHANNEL_URL)],
        [InlineKeyboardButton("✅ জয়েন ভেরিফাই করুন", callback_data="verify_join")],
        [InlineKeyboardButton("💬 জয় (JOY)-এর সাথে যোগাযোগ", url=OWNER_CONTACT_URL)],
    ])


def get_market_selection_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚡ 30 সেকেন্ড (30S)", callback_data="select_market_30S"),
            InlineKeyboardButton("⏱️ ১ মিনিট (1M)", callback_data="select_market_1M"),
        ],
        [
            InlineKeyboardButton("🕒 ৩ মিনিট (3M)", callback_data="select_market_3M"),
            InlineKeyboardButton("🕔 ৫ মিনিট (5M)", callback_data="select_market_5M"),
        ],
        [
            InlineKeyboardButton("👑 জয় (JOY) সম্পর্কে জানুন", callback_data="about_joy"),
            InlineKeyboardButton("💬 যোগাযোগ (@BDT588)", url=OWNER_CONTACT_URL),
        ],
    ])


def get_signal_control_keyboard(auto_on: bool) -> InlineKeyboardMarkup:
    toggle_btn = (
        InlineKeyboardButton("⏸️ অটো অফ করুন", callback_data="auto_off")
        if auto_on
        else InlineKeyboardButton("▶️ অটো অন করুন", callback_data="auto_on")
    )
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 নতুন সিগন্যাল নিন", callback_data="get_new_signal")],
        [toggle_btn, InlineKeyboardButton("🔄 মার্কেট পরিবর্তন", callback_data="change_market")],
        [
            InlineKeyboardButton("👑 জয় (JOY)", callback_data="about_joy"),
            InlineKeyboardButton("💬 যোগাযোগ (@BDT588)", url=OWNER_CONTACT_URL),
        ],
    ])


async def send_market_prompt(message_obj, user_name: str) -> None:
    text = (
        f"👑 **OWNER OF JOY — জয় (JOY)** 👑\n\n"
        f"স্বাগতম প্রিয় **{user_name}**! 🌟\n"
        f"এই সিস্টেমটি পরিচালনা করছেন **জয় (JOY)**। তিনি সবসময় চান ইউজাররা যেন একটি সুন্দর, পরিচ্ছন্ন এবং "
        f"দায়িত্বশীল অভিজ্ঞতা পান। **জয়**-এর বিশ্বাস—সঠিক গাইডলাইন, ধৈর্য এবং পরিশ্রম মানুষকে সঠিক পথে এগিয়ে নেয়।\n\n"
        f"📖 **শিক্ষামূলক ও মোটিভেশনাল বার্তা:**\n"
        f"• *তাড়াহুড়ো করে নয়, ভেবেচিন্তে ও ধৈর্য ধরে এগিয়ে চলুন—সময় ও শৃঙ্খলাই প্রকৃত সাফল্যের ভিত্তি।*\n"
        f"• *নিজের সামর্থ্য ও মানি ম্যানেজমেন্টের বাইরে কখনো যাবেন না; বুদ্ধিমত্তাই সবচেয়ে বড় পুঁজি।*\n\n"
        f"📞 **যেকোনো সমস্যা বা পরামর্শে যোগাযোগ করুন:** {OWNER_USERNAME}\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"👇 **আপনি কোন মার্কেটে ট্রেড করতে চান? নিচে থেকে সিলেক্ট করুন:**"
    )
    await message_obj.reply_text(text=text, parse_mode="Markdown", reply_markup=get_market_selection_keyboard())


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.message:
        return

    joined = await is_user_joined(user.id, context)
    if not joined:
        await update.message.reply_text(
            f"👑 **OWNER OF JOY — জয় (JOY)** 👑\n\n"
            f"🔒 **সিগন্যাল পেতে হলে আগে আমাদের টেলিগ্রাম চ্যানেলে জয়েন করতে হবে!**\n\n"
            f"নিচের বাটনে ক্লিক করে চ্যানেলে জয়েন করুন, তারপর **✅ জয়েন ভেরিফাই করুন** চাপুন।\n\n"
            f"📞 যেকোনো সমস্যা হলে **জয় (JOY)**-এর সাথে যোগাযোগ করুন: {OWNER_USERNAME}",
            parse_mode="Markdown",
            reply_markup=get_join_verify_keyboard(),
        )
        return

    user_states[user.id] = {
        "name": user.first_name,
        "market": None,
        "last_period": "",
        "last_pred": None,
        "auto": True,
    }
    await send_market_prompt(update.message, user.first_name)


async def market_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.message:
        return

    if not await is_user_joined(user.id, context):
        await update.message.reply_text(
            f"🔒 **আগে টেলিগ্রাম চ্যানেলে জয়েন করুন!**\n\nসমস্যা হলে **জয় (JOY)**-এর সাথে যোগাযোগ করুন: {OWNER_USERNAME}",
            parse_mode="Markdown",
            reply_markup=get_join_verify_keyboard(),
        )
        return

    await send_market_prompt(update.message, user.first_name)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 জয় (JOY)-এর সাথে যোগাযোগ করুন", url=OWNER_CONTACT_URL)],
        [InlineKeyboardButton("🔙 মার্কেট মেনুতে ফিরে যান", callback_data="change_market")],
    ])
    await update.message.reply_text(build_joy_about_message(), parse_mode="Markdown", reply_markup=keyboard)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user or not query.message:
        return

    user = query.from_user
    data = query.data or ""

    if data == "verify_join":
        joined = await is_user_joined(user.id, context)
        if joined:
            user_states[user.id] = {
                "name": user.first_name,
                "market": None,
                "last_period": "",
                "last_pred": None,
                "auto": True,
            }
            await query.answer("ভেরিফাই সফল! স্বাগতম ✅", show_alert=False)
            await send_market_prompt(query.message, user.first_name)
        else:
            await query.answer(
                f"আপনি এখনো চ্যানেলে জয়েন করেননি! আগে জয়েন করুন। সমস্যা হলে {OWNER_USERNAME} এ যোগাযোগ করুন।",
                show_alert=True,
            )
        return

    if not await is_user_joined(user.id, context):
        await query.answer("আগে চ্যানেলে জয়েন করুন!", show_alert=True)
        await query.message.reply_text(
            text=f"🔒 **আপনি চ্যানেলে জয়েন করেননি। আগে জয়েন করুন!**\n\nসমস্যা হলে যোগাযোগ: {OWNER_USERNAME}",
            parse_mode="Markdown",
            reply_markup=get_join_verify_keyboard(),
        )
        return

    state = user_states.setdefault(
        user.id,
        {"name": user.first_name, "market": None, "last_period": "", "last_pred": None, "auto": True},
    )
    state["name"] = user.first_name

    if data == "get_new_signal":
        market_key = state.get("market")
        if not isinstance(market_key, str) or market_key not in MARKETS:
            await query.answer("আগে একটি মার্কেট সিলেক্ট করুন!", show_alert=True)
            await send_market_prompt(query.message, user.first_name)
            return

        period, time_left = generate_market_period(market_key)
        prev_period = str(state.get("last_period") or "")
        prev_pred = state.get("last_pred")

        if prev_period and prev_period != period and isinstance(prev_pred, str) and prev_pred in ("BIG", "SMALL"):
            result_msg = format_result_announcement(
                user_name=user.first_name,
                market_key=market_key,
                finished_period=prev_period,
                predicted_type=prev_pred,
            )
            await query.message.reply_text(text=result_msg, parse_mode="Markdown")

        card, pred_type = format_market_signal_card(
            user.first_name,
            market_key,
            period,
            time_left,
            bool(state.get("auto", True)),
        )
        state["last_period"] = period
        state["last_pred"] = pred_type

        await query.answer("নতুন সিগন্যাল পাঠানো হয়েছে! 🔄", show_alert=False)
        await query.message.reply_text(
            text=card,
            parse_mode="Markdown",
            reply_markup=get_signal_control_keyboard(bool(state.get("auto", True))),
        )

    elif data == "about_joy":
        await query.answer("জয় (JOY) সম্পর্কে তথ্য")
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 জয় (JOY)-এর সাথে যোগাযোগ করুন", url=OWNER_CONTACT_URL)],
            [InlineKeyboardButton("🔙 মার্কেট সিলেক্ট করুন", callback_data="change_market")],
        ])
        await query.message.reply_text(text=build_joy_about_message(), parse_mode="Markdown", reply_markup=keyboard)

    elif data == "change_market":
        state["market"] = None
        state["last_period"] = ""
        state["last_pred"] = None
        await query.answer("মার্কেট সিলেক্ট করুন")
        await send_market_prompt(query.message, user.first_name)

    elif data.startswith("select_market_"):
        market_key = data.replace("select_market_", "", 1)
        if market_key not in MARKETS:
            return

        period, time_left = generate_market_period(market_key)
        card, pred_type = format_market_signal_card(user.first_name, market_key, period, time_left, True)

        state["market"] = market_key
        state["last_period"] = period
        state["last_pred"] = pred_type
        state["auto"] = True

        await query.answer(f"{market_key} মার্কেট সিলেক্ট হয়েছে!")
        await query.message.reply_text(
            text=card,
            parse_mode="Markdown",
            reply_markup=get_signal_control_keyboard(True),
        )

    elif data == "auto_off":
        state["auto"] = False
        await query.answer("অটো সিগন্যাল অফ করা হয়েছে ⏸️")
        await query.message.reply_text(
            text="⏸️ আপনার অটো সিগন্যাল সাময়িকভাবে বন্ধ করা হয়েছে। **🔄 নতুন সিগন্যাল নিন** বাটন চাপলে নতুন সিগন্যাল পাবেন।",
            parse_mode="Markdown",
            reply_markup=get_signal_control_keyboard(False),
        )

    elif data == "auto_on":
        state["auto"] = True
        await query.answer("অটো সিগন্যাল অন করা হয়েছে ▶️")
        market_key = state.get("market")
        if isinstance(market_key, str) and market_key in MARKETS:
            period, time_left = generate_market_period(market_key)
            card, pred_type = format_market_signal_card(user.first_name, market_key, period, time_left, True)
            state["last_period"] = period
            state["last_pred"] = pred_type
            await query.message.reply_text(
                text=card,
                parse_mode="Markdown",
                reply_markup=get_signal_control_keyboard(True),
            )


async def auto_market_signal_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    if not user_states:
        return

    for user_id, state in list(user_states.items()):
        market_key = state.get("market")
        auto_on = bool(state.get("auto", True))
        if not auto_on or not isinstance(market_key, str) or market_key not in MARKETS:
            continue

        current_period, time_left = generate_market_period(market_key)
        prev_period = str(state.get("last_period") or "")
        prev_pred = state.get("last_pred")

        if prev_period and prev_period != current_period:
            if not await is_user_joined(user_id, context):
                state["market"] = None
                continue

            user_name = str(state.get("name") or "Trader")
            try:
                if isinstance(prev_pred, str) and prev_pred in ("BIG", "SMALL"):
                    result_msg = format_result_announcement(
                        user_name=user_name,
                        market_key=market_key,
                        finished_period=prev_period,
                        predicted_type=prev_pred,
                    )
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=result_msg,
                        parse_mode="Markdown",
                    )

                new_card, new_pred = format_market_signal_card(
                    user_name=user_name,
                    market_key=market_key,
                    period=current_period,
                    time_left=time_left,
                    auto_on=True,
                )
                state["last_period"] = current_period
                state["last_pred"] = new_pred

                await context.bot.send_message(
                    chat_id=user_id,
                    text=new_card,
                    parse_mode="Markdown",
                    reply_markup=get_signal_control_keyboard(True),
                )
            except Exception as e:
                logger.error(f"Error auto pushing signal to user {user_id}: {e}")


def main() -> None:
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("market", market_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CallbackQueryHandler(callback_handler))

    if app.job_queue:
        app.job_queue.run_repeating(auto_market_signal_job, interval=2, first=2)
        logger.info("JobQueue auto_market_signal_job scheduled.")
    else:
        logger.warning("JobQueue is not available. Add python-telegram-bot[job-queue] to requirements.txt.")

    logger.info("OWNER OF JOY — জয় (JOY) VIP Signal Bot started...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
