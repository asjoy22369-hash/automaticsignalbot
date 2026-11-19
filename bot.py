import logging
from datetime import datetime, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
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

# কয়েন ডিপোজিট ও রেফারেল কনফিগারেশন (প্রয়োজন অনুযায়ী অ্যাড্রেস ও মান বদলে নিবি)
MIN_COIN_DEPOSIT = "10 USDT"
COIN_WALLETS_INFO = (
    "• **USDT (TRC20):** `TYourTRC20WalletAddressHere`\n"
    "• **USDT (BEP20):** `0xYourBEP20WalletAddressHere`\n"
    "• **TRX (TRON):** `TYourTRXWalletAddressHere`"
)
REFERRAL_BONUS_PER_USER = 50

# মার্কেট কনফিগারেশন: key -> (display_label, duration_seconds, base_offset)
MARKETS: dict[str, tuple[str, int, int]] = {
    "30S": ("30S (৩০ সেকেন্ড)", 30, 50000),
    "1M": ("1M (১ মিনিট)", 60, 20000),
    "3M": ("3M (৩ মিনিট)", 180, 10000),
    "5M": ("5M (৫ মিনিট)", 300, 5000),
}

# ইউজার স্টেট ট্র্যাক করার ডিকশনারি
user_states: dict[int, dict[str, object]] = {}


def get_or_create_user(user_id: int, user_name: str, referred_by: int | None = None) -> dict[str, object]:
    state = user_states.get(user_id)
    if state is None:
        state = {
            "name": user_name,
            "market": None,
            "last_period": "",
            "last_pred": None,
            "referred_by": referred_by,
            "referrals": [],
            "referral_bonus": 0,
            "deposits": [],
            "awaiting_deposit": False,
        }
        user_states[user_id] = state
    else:
        state["name"] = user_name
        if referred_by is not None and state.get("referred_by") is None and referred_by != user_id:
            state["referred_by"] = referred_by
    return state


def apply_referral_credit(referrer_id: int | None, new_user_id: int) -> None:
    if not referrer_id or referrer_id == new_user_id:
        return
    referrer_state = user_states.get(referrer_id)
    if not referrer_state:
        return

    refs = referrer_state.setdefault("referrals", [])
    if isinstance(refs, list) and new_user_id not in refs:
        refs.append(new_user_id)
        current_bonus = int(referrer_state.get("referral_bonus", 0) or 0)
        referrer_state["referral_bonus"] = current_bonus + REFERRAL_BONUS_PER_USER
        logger.info(f"Referral credited: referrer={referrer_id}, new_user={new_user_id}")


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
        f"❌ **𝐒𝐓𝐀𝐓𝐔𝐒** ➤ **LOSS**\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"🚀 *নতুন সিগন্যাল নিচে দেওয়া হলো 👇*"
    )


def format_market_signal_card(
    user_name: str,
    market_key: str,
    period: str,
    time_left: int,
) -> tuple[str, str]:
    market_label, _, _ = MARKETS[market_key]
    pred_type, action_text, color_text, lucky_num = generate_signal_for_market(market_key, period)

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
        f"📞 *Contact:* {OWNER_USERNAME}"
    )
    return card, pred_type


async def build_referral_message(user_id: int, user_name: str, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot_info = await context.bot.get_me()
    bot_username = bot_info.username or "YourBotUsername"
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"

    state = get_or_create_user(user_id, user_name)
    refs = state.get("referrals", [])
    ref_count = len(refs) if isinstance(refs, list) else 0
    bonus = int(state.get("referral_bonus", 0) or 0)

    return (
        f"👥 **রেফারেল সিস্টেম — জয় (JOY)** 👥\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"👤 *Member:* `{user_name}`\n"
        f"🔗 *আপনার রেফারেল লিংক:*\n`{ref_link}`\n\n"
        f"📊 *মোট রেফারেল:* **{ref_count} জন**\n"
        f"🎁 *মোট রেফার বোনাস:* **{bonus} Coin / Credit**\n"
        f"✨ *প্রতি সফল রেফারে বোনাস:* **{REFERRAL_BONUS_PER_USER} Coin / Credit**\n\n"
        f"📞 *Contact:* {OWNER_USERNAME}"
    )


def build_coin_deposit_message(user_id: int, user_name: str) -> str:
    state = get_or_create_user(user_id, user_name)
    deposits = state.get("deposits", [])
    dep_count = len(deposits) if isinstance(deposits, list) else 0

    return (
        f"🪙 **কয়েনের মাধ্যমে ডিপোজিট করুন — জয় (JOY)** 🪙\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"👤 *User:* `{user_name}` (`ID: {user_id}`)\n"
        f"💰 *সর্বনিম্ন কয়েন ডিপোজিট:* **{MIN_COIN_DEPOSIT}**\n"
        f"🧾 *জমা দেওয়া কয়েন ডিপোজিট রিকোয়েস্ট:* **{dep_count}টি**\n\n"
        f"🌐 **কয়েন ওয়ালেট অ্যাড্রেসসমূহ:**\n"
        f"{COIN_WALLETS_INFO}\n\n"
        f"📝 **কয়েনে ডিপোজিট করার নিয়ম:**\n"
        f"১. সঠিক কয়েন ও সঠিক নেটওয়ার্ক সিলেক্ট করে উপরের ওয়ালেট অ্যাড্রেসে কয়েন পাঠান।\n"
        f"২. নিচের **✍️ কয়েন ডিপোজিট তথ্য জমা দিন** বাটনে চাপ দিয়ে **কয়েনের নাম, অ্যামাউন্ট ও TxID/Hash** লিখে পাঠান (যেমন: `20 USDT TRC20 TxID: 9a8b7c6d`)।\n"
        f"৩. প্রয়োজনে যোগাযোগ করুন: {OWNER_USERNAME}"
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
        [InlineKeyboardButton("💬 যোগাযোগ (@BDT588)", url=OWNER_CONTACT_URL)],
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
            InlineKeyboardButton("🪙 কয়েনের মাধ্যমে ডিপোজিট করুন", callback_data="open_coin_deposit"),
            InlineKeyboardButton("👥 রেফারেল সিস্টেম", callback_data="open_referral"),
        ],
        [InlineKeyboardButton("💬 যোগাযোগ (@BDT588)", url=OWNER_CONTACT_URL)],
    ])


def get_signal_control_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 নতুন সিগন্যাল নিন", callback_data="get_new_signal")],
        [
            InlineKeyboardButton("🔄 মার্কেট পরিবর্তন", callback_data="change_market"),
            InlineKeyboardButton("👥 রেফারেল সিস্টেম", callback_data="open_referral"),
        ],
        [
            InlineKeyboardButton("🪙 কয়েনের মাধ্যমে ডিপোজিট করুন", callback_data="open_coin_deposit"),
            InlineKeyboardButton("💬 যোগাযোগ (@BDT588)", url=OWNER_CONTACT_URL),
        ],
    ])


def get_coin_deposit_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✍️ কয়েন ডিপোজিট তথ্য জমা দিন", callback_data="submit_coin_deposit")],
        [InlineKeyboardButton("💬 যোগাযোগ (@BDT588)", url=OWNER_CONTACT_URL)],
        [InlineKeyboardButton("🔙 মার্কেট মেনুতে ফিরে যান", callback_data="change_market")],
    ])


def get_referral_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🪙 কয়েনের মাধ্যমে ডিপোজিট করুন", callback_data="open_coin_deposit")],
        [InlineKeyboardButton("💬 যোগাযোগ (@BDT588)", url=OWNER_CONTACT_URL)],
        [InlineKeyboardButton("🔙 মার্কেট মেনুতে ফিরে যান", callback_data="change_market")],
    ])


async def send_market_prompt(message_obj, user_name: str) -> None:
    text = (
        f"👑 **OWNER OF JOY — জয় (JOY)** 👑\n\n"
        f"স্বাগতম **{user_name}**! 🌟\n"
        f"পরিচালনায়: **জয় (JOY)** | যোগাযোগ: {OWNER_USERNAME}\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"👇 **আপনি কোন মার্কেটে ট্রেড করতে চান? নিচে থেকে সিলেক্ট করুন:**"
    )
    await message_obj.reply_text(text=text, parse_mode="Markdown", reply_markup=get_market_selection_keyboard())


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.message:
        return

    referrer_id: int | None = None
    if context.args:
        arg = context.args[0].strip()
        if arg.startswith("ref_"):
            raw_ref = arg.replace("ref_", "", 1)
            if raw_ref.isdigit() and int(raw_ref) != user.id:
                referrer_id = int(raw_ref)

    state = get_or_create_user(user.id, user.first_name, referred_by=referrer_id)
    if referrer_id is not None:
        apply_referral_credit(referrer_id, user.id)

    joined = await is_user_joined(user.id, context)
    if not joined:
        await update.message.reply_text(
            f"👑 **OWNER OF JOY — জয় (JOY)** 👑\n\n"
            f"🔒 **সিগন্যাল পেতে হলে আগে আমাদের টেলিগ্রাম চ্যানেলে জয়েন করতে হবে!**\n\n"
            f"নিচের বাটনে ক্লিক করে চ্যানেলে জয়েন করুন, তারপর **✅ জয়েন ভেরিফাই করুন** চাপুন।\n\n"
            f"📞 যোগাযোগ: {OWNER_USERNAME}",
            parse_mode="Markdown",
            reply_markup=get_join_verify_keyboard(),
        )
        return

    state["market"] = None
    state["last_period"] = ""
    state["last_pred"] = None
    state["awaiting_deposit"] = False
    await send_market_prompt(update.message, user.first_name)


async def market_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.message:
        return

    if not await is_user_joined(user.id, context):
        await update.message.reply_text(
            f"🔒 **আগে টেলিগ্রাম চ্যানেলে জয়েন করুন!**\n\nযোগাযোগ: {OWNER_USERNAME}",
            parse_mode="Markdown",
            reply_markup=get_join_verify_keyboard(),
        )
        return

    await send_market_prompt(update.message, user.first_name)


async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.message:
        return

    msg = await build_referral_message(user.id, user.first_name, context)
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_referral_keyboard())


async def deposit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.message:
        return

    msg = build_coin_deposit_message(user.id, user.first_name)
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_coin_deposit_keyboard())


async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.message or not update.message.text:
        return

    state = get_or_create_user(user.id, user.first_name)
    if bool(state.get("awaiting_deposit", False)):
        raw_text = update.message.text.strip()
        deposits = state.setdefault("deposits", [])
        if isinstance(deposits, list):
            deposits.append({
                "details": raw_text,
                "submitted_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            })
        state["awaiting_deposit"] = False
        logger.info(f"Coin deposit submitted by user {user.id} ({user.first_name}): {raw_text}")

        confirm_text = (
            f"✅ **কয়েন ডিপোজিট তথ্য গ্রহণ করা হয়েছে!** ✅\n"
            f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
            f"👤 *User:* `{user.first_name}` (`ID: {user.id}`)\n"
            f"🪙 *জমা দেওয়া কয়েন তথ্য:* `{raw_text}`\n\n"
            f"📞 যোগাযোগ: {OWNER_USERNAME}"
        )
        await update.message.reply_text(
            confirm_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 যোগাযোগ (@BDT588)", url=OWNER_CONTACT_URL)],
                [InlineKeyboardButton("🔙 মার্কেট মেনুতে ফিরে যান", callback_data="change_market")],
            ]),
        )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user or not query.message:
        return

    user = query.from_user
    data = query.data or ""

    if data == "verify_join":
        joined = await is_user_joined(user.id, context)
        if joined:
            state = get_or_create_user(user.id, user.first_name)
            state["market"] = None
            state["last_period"] = ""
            state["last_pred"] = None
            await query.answer("ভেরিফাই সফল! স্বাগতম ✅", show_alert=False)
            await send_market_prompt(query.message, user.first_name)
        else:
            await query.answer(
                f"আপনি এখনো চ্যানেলে জয়েন করেননি! আগে জয়েন করুন। সমস্যা হলে {OWNER_USERNAME} এ যোগাযোগ করুন।",
                show_alert=True,
            )
        return

    state = get_or_create_user(user.id, user.first_name)

    if data == "open_referral":
        await query.answer("রেফারেল সিস্টেম")
        msg = await build_referral_message(user.id, user.first_name, context)
        await query.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_referral_keyboard())
        return

    if data == "open_coin_deposit":
        await query.answer("কয়েনের মাধ্যমে ডিপোজিট")
        msg = build_coin_deposit_message(user.id, user.first_name)
        await query.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_coin_deposit_keyboard())
        return

    if data == "submit_coin_deposit":
        state["awaiting_deposit"] = True
        await query.answer("কয়েন ডিপোজিট তথ্য লিখুন")
        await query.message.reply_text(
            f"✍️ **আপনি কোন কয়েনে কত পাঠিয়েছেন এবং TxID/Hash লিখে পাঠান:**\n\n"
            f"উদাহরণ: `20 USDT TRC20 - TxID: 8f92e1a04b`\n\n"
            f"📞 প্রয়োজনে যোগাযোগ করুন: {OWNER_USERNAME}",
            parse_mode="Markdown",
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
        )
        state["last_period"] = period
        state["last_pred"] = pred_type

        await query.answer("নতুন সিগন্যাল পাঠানো হয়েছে! 🔄", show_alert=False)
        await query.message.reply_text(
            text=card,
            parse_mode="Markdown",
            reply_markup=get_signal_control_keyboard(),
        )

    elif data == "change_market":
        state["market"] = None
        state["last_period"] = ""
        state["last_pred"] = None
        state["awaiting_deposit"] = False
        await query.answer("মার্কেট সিলেক্ট করুন")
        await send_market_prompt(query.message, user.first_name)

    elif data.startswith("select_market_"):
        market_key = data.replace("select_market_", "", 1)
        if market_key not in MARKETS:
            return

        period, time_left = generate_market_period(market_key)
        card, pred_type = format_market_signal_card(user.first_name, market_key, period, time_left)

        state["market"] = market_key
        state["last_period"] = period
        state["last_pred"] = pred_type

        await query.answer(f"{market_key} মার্কেট সিলেক্ট হয়েছে!")
        await query.message.reply_text(
            text=card,
            parse_mode="Markdown",
            reply_markup=get_signal_control_keyboard(),
        )


def main() -> None:
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("market", market_command))
    app.add_handler(CommandHandler("referral", referral_command))
    app.add_handler(CommandHandler("deposit", deposit_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))

    logger.info("OWNER OF JOY — জয় (JOY) VIP Signal Bot with Coin Deposit started...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
