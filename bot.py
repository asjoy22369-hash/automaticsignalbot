import logging
from datetime import datetime, timezone
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
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

TOKEN = "9049655726:AAGhdmogKzkYOsyzJs-cv-6mtP7pY0PVtWA"
CHANNEL_ID = "@bdincomesitehgnice"
CHANNEL_URL = "https://t.me/bdincomesitehgnice"
OWNER_USERNAME = "@BDT588"
OWNER_CONTACT_URL = "https://t.me/BDT588"

# ইউজার ফ্রি ডিপোজিট রিকোয়েস্ট পাঠালে সরাসরি তোর অ্যাকাউন্টে যাওয়ার জন্য তোর নিউমেরিক Telegram User ID বসা
OWNER_CHAT_ID: int = 0

FREE_DEPOSIT_REQUEST_TEXT = "আমার 10,000 টোকেন হয়েছে আমাকে ফ্রি ডিপোজিট দিন"

# ডেসক্রিপশনের ওপরে দেখানোর হেডিং
TOP_SYSTEM_BANNER = "⚡ **ডিকে উইন এইজ নাইস সিগন্যাল সিস্টেম** ⚡"

# বট স্টার্ট বা ওপেন করার সাথে সাথেই ওপরে দেখানোর সুন্দর ডেসক্রিপশন
BOT_TOP_DESCRIPTION = (
    f"{TOP_SYSTEM_BANNER}\n"
    f"👑 **OWNER OF JOY — জয় (JOY)** 👑\n"
    f"✨ আমি **OWNER OF JOY** (জয়)-এর একজন বুদ্ধিমত্তা সিস্টেম। ✨\n\n"
    f"🌟 **OWNER OF JOY** বিশ্বাস করেন—ধৈর্য, শৃঙ্খলা এবং শান্ত মাথায় নেওয়া সঠিক সিদ্ধান্তই মানুষকে প্রকৃত সাফল্যের শিখরে পৌঁছে দেয়। "
    f"তাড়াহুড়ো বা আবেগ নয়, বরং বুদ্ধিমত্তা ও আত্মবিশ্বাস নিয়ে প্রতিটি পদক্ষেপ নিন। "
    f"**OWNER OF JOY** সবসময় চান আপনি নিজের ওপর বিশ্বাস রেখে ধাপে ধাপে এগিয়ে যান, "
    f"কারণ **OWNER OF JOY**-এর দেখানো সাফল্যের পথ গড়ে ওঠে নিয়মানুবর্তিতা ও পরিশ্রমের ভেতর দিয়ে।\n\n"
    f"📊 **Markets:** `30S` • `1M` • `3M` • `5M`\n"
    f"📞 **Contact:** @BDT588"
)

# কয়েন ডিপোজিট ও রেফারেল কনফিগারেশন
MIN_COIN_DEPOSIT = "10 USDT"
COIN_WALLETS_INFO = (
    "• **USDT (TRC20):** `TYourTRC20WalletAddressHere`\n"
    "• **USDT (BEP20):** `0xYourBEP20WalletAddressHere`\n"
    "• **TRX (TRON):** `TYourTRXWalletAddressHere`"
)
REFERRAL_BONUS_PER_USER = 100
FREE_DEPOSIT_TARGET_COINS = 10000

# মার্কেট কনফিগারেশন: key -> (display_label, duration_seconds, base_offset)
MARKETS: dict[str, tuple[str, int, int]] = {
    "30S": ("30S (৩০ সেকেন্ড)", 30, 50000),
    "1M": ("1M (১ মিনিট)", 60, 20000),
    "3M": ("3M (৩ মিনিট)", 180, 10000),
    "5M": ("5M (৫ মিনিট)", 300, 5000),
}

# নিচের কীবোর্ড বাটন লেবেলসমূহ
BTN_MENU_OPEN = "☰ মেনু"
BTN_MENU_CLOSE = "✕ মেনু বন্ধ"
BTN_30S = "⚡ 30S"
BTN_1M = "⏱️ 1M"
BTN_3M = "🕒 3M"
BTN_5M = "🕔 5M"
BTN_NEW_SIGNAL = "🔄 নতুন সিগন্যাল নিন"
BTN_CHANGE_MARKET = "🔄 মার্কেট পরিবর্তন"
BTN_REFERRAL = "👥 রেফারেল সিস্টেম"
BTN_COIN_DEPOSIT = "🪙 কয়েনের মাধ্যমে ডিপোজিট করুন"
BTN_SUBMIT_DEPOSIT = "✍️ কয়েন ডিপোজিট তথ্য জমা দিন"
BTN_FREE_DEPOSIT = "🎁 ফ্রি ডিপোজিট নিন (10,000 কয়েন)"
BTN_BACK = "⬅️ Back"

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
            "free_deposits_claimed": 0,
            "deposits": [],
            "awaiting_deposit": False,
            "current_view": "market_menu",
            "nav_stack": [],
            "menu_expanded": False,
        }
        user_states[user_id] = state
    else:
        state["name"] = user_name
        state.setdefault("nav_stack", [])
        state.setdefault("current_view", "market_menu")
        state.setdefault("menu_expanded", False)
        if referred_by is not None and state.get("referred_by") is None and referred_by != user_id:
            state["referred_by"] = referred_by
    return state


def push_navigation_view(state: dict[str, object], next_view: str) -> None:
    current = str(state.get("current_view") or "market_menu")
    stack = state.setdefault("nav_stack", [])
    if isinstance(stack, list) and current != next_view:
        stack.append(current)
    state["current_view"] = next_view


def pop_navigation_view(state: dict[str, object]) -> str:
    stack = state.setdefault("nav_stack", [])
    if isinstance(stack, list) and stack:
        prev_view = str(stack.pop())
        state["current_view"] = prev_view
        return prev_view
    state["current_view"] = "market_menu"
    return "market_menu"


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
        logger.info(
            f"Referral credited (+{REFERRAL_BONUS_PER_USER} coins): referrer={referrer_id}, new_user={new_user_id}"
        )


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
    coins = int(state.get("referral_bonus", 0) or 0)
    claimed = int(state.get("free_deposits_claimed", 0) or 0)

    return (
        f"👥 **রেফারেল সিস্টেম — জয় (JOY)** 👥\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"👤 *Member:* `{user_name}`\n"
        f"🔗 *আপনার রেফারেল লিংক:*\n`{ref_link}`\n\n"
        f"📊 *মোট রেফারেল:* **{ref_count} জন**\n"
        f"🪙 *বর্তমান কয়েন ব্যালেন্স:* **{coins:,} কয়েন**\n"
        f"✨ *প্রতি ১টি রেফারে পাবেন:* **{REFERRAL_BONUS_PER_USER} কয়েন**\n"
        f"🎁 *ফ্রি ডিপোজিট টার্গেট:* **{FREE_DEPOSIT_TARGET_COINS:,} কয়েন**\n"
        f"🆓 *নেওয়া ফ্রি ডিপোজিট:* **{claimed}টি**\n\n"
        f"📞 *Contact:* {OWNER_USERNAME}"
    )


def build_coin_deposit_message(user_id: int, user_name: str) -> str:
    state = get_or_create_user(user_id, user_name)
    deposits = state.get("deposits", [])
    dep_count = len(deposits) if isinstance(deposits, list) else 0
    coins = int(state.get("referral_bonus", 0) or 0)

    return (
        f"🪙 **কয়েনের মাধ্যমে ডিপোজিট করুন — জয় (JOY)** 🪙\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"👤 *User:* `{user_name}` (`ID: {user_id}`)\n"
        f"💰 *সর্বনিম্ন কয়েন ডিপোজিট:* **{MIN_COIN_DEPOSIT}**\n"
        f"🪙 *আপনার রেফারেল কয়েন:* **{coins:,} / {FREE_DEPOSIT_TARGET_COINS:,} কয়েন**\n"
        f"🧾 *জমা দেওয়া কয়েন ডিপোজিট রিকোয়েস্ট:* **{dep_count}টি**\n\n"
        f"🌐 **কয়েন ওয়ালেট অ্যাড্রেসসমূহ:**\n"
        f"{COIN_WALLETS_INFO}\n\n"
        f"📝 **ডিপোজিট করার নিয়ম:**\n"
        f"১. সঠিক কয়েন ও সঠিক নেটওয়ার্ক সিলেক্ট করে উপরের ওয়ালেট অ্যাড্রেসে কয়েন পাঠান।\n"
        f"২. নিচের মেনু থেকে **{BTN_SUBMIT_DEPOSIT}** চাপ দিয়ে **কয়েনের নাম, অ্যামাউন্ট ও TxID/Hash** লিখে পাঠান।\n"
        f"৩. ফ্রি ডিপোজিট নিতে চাইলে **{BTN_FREE_DEPOSIT}** চাপুন।\n"
        f"📞 যোগাযোগ: {OWNER_USERNAME}"
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


def get_bottom_menu_keyboard(state: dict[str, object]) -> ReplyKeyboardMarkup:
    view_name = str(state.get("current_view") or "market_menu")
    menu_expanded = bool(state.get("menu_expanded", False))
    stack = state.get("nav_stack", [])
    has_prev = isinstance(stack, list) and len(stack) > 0

    if not menu_expanded:
        top_row = [KeyboardButton(BTN_NEW_SIGNAL), KeyboardButton(BTN_MENU_OPEN)] if view_name == "signal_view" else [KeyboardButton(BTN_MENU_OPEN)]
        rows = [top_row]
        if has_prev:
            rows.append([KeyboardButton(BTN_BACK)])
        return ReplyKeyboardMarkup(
            rows,
            resize_keyboard=True,
            is_persistent=True,
            input_field_placeholder="☰ মেনু বাটনে ক্লিক করে অপশন চালু করুন...",
        )

    if view_name == "signal_view":
        rows = [
            [KeyboardButton(BTN_NEW_SIGNAL)],
            [KeyboardButton(BTN_30S), KeyboardButton(BTN_1M), KeyboardButton(BTN_3M), KeyboardButton(BTN_5M)],
            [KeyboardButton(BTN_CHANGE_MARKET), KeyboardButton(BTN_REFERRAL)],
            [KeyboardButton(BTN_COIN_DEPOSIT)],
        ]
    elif view_name in ("deposit_view", "referral_view"):
        rows = [
            [KeyboardButton(BTN_SUBMIT_DEPOSIT)],
            [KeyboardButton(BTN_FREE_DEPOSIT)],
            [KeyboardButton(BTN_REFERRAL), KeyboardButton(BTN_COIN_DEPOSIT)],
            [KeyboardButton(BTN_30S), KeyboardButton(BTN_1M), KeyboardButton(BTN_3M), KeyboardButton(BTN_5M)],
        ]
    else:
        rows = [
            [KeyboardButton(BTN_30S), KeyboardButton(BTN_1M), KeyboardButton(BTN_3M), KeyboardButton(BTN_5M)],
            [KeyboardButton(BTN_COIN_DEPOSIT), KeyboardButton(BTN_REFERRAL)],
        ]

    control_row = [KeyboardButton(BTN_MENU_CLOSE)]
    if has_prev:
        control_row.append(KeyboardButton(BTN_BACK))
    rows.append(control_row)

    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="অপশন সিলেক্ট করুন অথবা ✕ মেনু বন্ধ চাপুন...",
    )


async def send_market_prompt(message_obj, user_name: str, state: dict[str, object]) -> None:
    text = (
        f"{BOT_TOP_DESCRIPTION}\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"স্বাগতম **{user_name}**! 🌟\n"
        f"আপনি কয় সেকেন্ডে ট্রেড করতে চান? আপনি ১ মিনিটে (`1M`) না ৩০ সেকেন্ডে (`30S`)—অপশন চালু করতে নিচের `{BTN_MENU_OPEN}` বাটনে ক্লিক করুন:"
    )
    await message_obj.reply_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=get_bottom_menu_keyboard(state),
    )


async def render_view(
    view_name: str,
    message_obj,
    user_id: int,
    user_name: str,
    state: dict[str, object],
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if view_name == "referral_view":
        msg = await build_referral_message(user_id, user_name, context)
        await message_obj.reply_text(
            msg,
            parse_mode="Markdown",
            reply_markup=get_bottom_menu_keyboard(state),
        )
        return

    if view_name == "deposit_view":
        msg = build_coin_deposit_message(user_id, user_name)
        await message_obj.reply_text(
            msg,
            parse_mode="Markdown",
            reply_markup=get_bottom_menu_keyboard(state),
        )
        return

    if view_name == "submit_deposit_view":
        state["awaiting_deposit"] = True
        await message_obj.reply_text(
            f"✍️ **আপনি কোন কয়েনে কত পাঠিয়েছেন এবং TxID/Hash লিখে পাঠান:**\n\n"
            f"উদাহরণ: `20 USDT TRC20 - TxID: 8f92e1a04b`\n\n"
            f"📞 প্রয়োজনে যোগাযোগ করুন: {OWNER_USERNAME}",
            parse_mode="Markdown",
            reply_markup=get_bottom_menu_keyboard(state),
        )
        return

    if view_name == "free_deposit_view":
        await message_obj.reply_text(
            f"`{FREE_DEPOSIT_REQUEST_TEXT}`\n\n"
            f"👆 এই লেখাটি কপি করে সেন্ড করুন, সাথে সাথে **জয় (JOY)**-এর কাছে চলে যাবে এবং রিপ্লাই দিয়ে ফ্রি ডিপোজিট পাবেন।",
            parse_mode="Markdown",
            reply_markup=get_bottom_menu_keyboard(state),
        )
        return

    if view_name == "signal_view":
        market_key = state.get("market")
        if isinstance(market_key, str) and market_key in MARKETS:
            period, time_left = generate_market_period(market_key)
            card, pred_type = format_market_signal_card(user_name, market_key, period, time_left)
            state["last_period"] = period
            state["last_pred"] = pred_type
            await message_obj.reply_text(
                text=card,
                parse_mode="Markdown",
                reply_markup=get_bottom_menu_keyboard(state),
            )
            return

    state["current_view"] = "market_menu"
    await send_market_prompt(message_obj, user_name, state)


async def open_selected_market(
    market_key: str,
    message_obj,
    user_name: str,
    state: dict[str, object],
) -> None:
    period, time_left = generate_market_period(market_key)
    card, pred_type = format_market_signal_card(user_name, market_key, period, time_left)

    state["market"] = market_key
    state["last_period"] = period
    state["last_pred"] = pred_type
    state["menu_expanded"] = False
    push_navigation_view(state, "signal_view")

    await message_obj.reply_text(
        text=card,
        parse_mode="Markdown",
        reply_markup=get_bottom_menu_keyboard(state),
    )


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
            f"{BOT_TOP_DESCRIPTION}\n"
            f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
            f"🔒 **সিগন্যাল পেতে হলে আগে আমাদের টেলিগ্রাম চ্যানেলে জয়েন করতে হবে!**\n\n"
            f"নিচের বাটনে ক্লিক করে চ্যানেলে জয়েন করুন, তারপর **✅ জয়েন ভেরিফাই করুন** চাপুন।",
            parse_mode="Markdown",
            reply_markup=get_join_verify_keyboard(),
        )
        return

    state["market"] = None
    state["last_period"] = ""
    state["last_pred"] = None
    state["awaiting_deposit"] = False
    state["current_view"] = "market_menu"
    state["nav_stack"] = []
    state["menu_expanded"] = False
    await send_market_prompt(update.message, user.first_name, state)


async def market_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.message:
        return

    if not await is_user_joined(user.id, context):
        await update.message.reply_text(
            f"{BOT_TOP_DESCRIPTION}\n"
            f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
            f"🔒 **আগে টেলিগ্রাম চ্যানেলে জয়েন করুন!**",
            parse_mode="Markdown",
            reply_markup=get_join_verify_keyboard(),
        )
        return

    state = get_or_create_user(user.id, user.first_name)
    state["menu_expanded"] = True
    push_navigation_view(state, "market_menu")
    await send_market_prompt(update.message, user.first_name, state)


async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.message:
        return

    state = get_or_create_user(user.id, user.first_name)
    push_navigation_view(state, "referral_view")
    msg = await build_referral_message(user.id, user.first_name, context)
    await update.message.reply_text(
        msg,
        parse_mode="Markdown",
        reply_markup=get_bottom_menu_keyboard(state),
    )


async def deposit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.message:
        return

    state = get_or_create_user(user.id, user.first_name)
    push_navigation_view(state, "deposit_view")
    msg = build_coin_deposit_message(user.id, user.first_name)
    await update.message.reply_text(
        msg,
        parse_mode="Markdown",
        reply_markup=get_bottom_menu_keyboard(state),
    )


async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.message or not update.message.text:
        return

    raw_text = update.message.text.strip()
    state = get_or_create_user(user.id, user.first_name)

    if raw_text == FREE_DEPOSIT_REQUEST_TEXT:
        claimed = int(state.get("free_deposits_claimed", 0) or 0) + 1
        state["free_deposits_claimed"] = claimed
        logger.info(f"Free deposit text sent by user {user.id} ({user.first_name})")

        if OWNER_CHAT_ID:
            try:
                owner_alert = (
                    f"🎁 **ফ্রি ডিপোজিট রিকোয়েস্ট এসেছে!** 🎁\n"
                    f"👤 *User:* `{user.first_name}` (`ID: {user.id}`)\n"
                    f"💬 *মেসেজ:* `{raw_text}`\n"
                    f"📌 *এই মেসেজের রিপ্লাই দিয়ে ফ্রি ডিপোজিট দিন।*"
                )
                await context.bot.send_message(
                    chat_id=OWNER_CHAT_ID,
                    text=owner_alert,
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error(f"Failed to forward free deposit request to owner: {e}")

        await update.message.reply_text(
            f"✅ আপনার রিকোয়েস্ট পাঠানো হয়েছে!\n"
            f"খুব শীঘ্রই **জয় (JOY)** আপনার মেসেজের রিপ্লাই দিয়ে ফ্রি ডিপোজিট দিয়ে দেবেন।\n"
            f"📞 যোগাযোগ: {OWNER_USERNAME}",
            parse_mode="Markdown",
            reply_markup=get_bottom_menu_keyboard(state),
        )
        return

    if bool(state.get("awaiting_deposit", False)) and raw_text not in {
        BTN_MENU_OPEN,
        BTN_MENU_CLOSE,
        BTN_BACK,
        BTN_CHANGE_MARKET,
        BTN_REFERRAL,
        BTN_COIN_DEPOSIT,
        BTN_FREE_DEPOSIT,
        BTN_NEW_SIGNAL,
        BTN_30S,
        BTN_1M,
        BTN_3M,
        BTN_5M,
    }:
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
            reply_markup=get_bottom_menu_keyboard(state),
        )
        return

    if raw_text == BTN_MENU_OPEN:
        state["menu_expanded"] = True
        await update.message.reply_text(
            "☰ **মেনু চালু হয়েছে!** নিচে থেকে আপনার প্রয়োজনীয় অপশন সিলেক্ট করুন:",
            parse_mode="Markdown",
            reply_markup=get_bottom_menu_keyboard(state),
        )
        return

    if raw_text == BTN_MENU_CLOSE:
        state["menu_expanded"] = False
        await update.message.reply_text(
            f"✕ **মেনু গুটিয়ে নেওয়া হয়েছে।** আবার অপশন চাইলে `{BTN_MENU_OPEN}` চাপুন।",
            parse_mode="Markdown",
            reply_markup=get_bottom_menu_keyboard(state),
        )
        return

    if raw_text == BTN_BACK:
        state["awaiting_deposit"] = False
        prev_view = pop_navigation_view(state)
        await render_view(prev_view, update.message, user.id, user.first_name, state, context)
        return

    if raw_text == BTN_REFERRAL:
        state["menu_expanded"] = False
        push_navigation_view(state, "referral_view")
        msg = await build_referral_message(user.id, user.first_name, context)
        await update.message.reply_text(
            msg,
            parse_mode="Markdown",
            reply_markup=get_bottom_menu_keyboard(state),
        )
        return

    if raw_text == BTN_COIN_DEPOSIT:
        state["menu_expanded"] = False
        push_navigation_view(state, "deposit_view")
        msg = build_coin_deposit_message(user.id, user.first_name)
        await update.message.reply_text(
            msg,
            parse_mode="Markdown",
            reply_markup=get_bottom_menu_keyboard(state),
        )
        return

    if raw_text == BTN_SUBMIT_DEPOSIT:
        state["menu_expanded"] = False
        push_navigation_view(state, "submit_deposit_view")
        state["awaiting_deposit"] = True
        await update.message.reply_text(
            f"✍️ **আপনি কোন কয়েনে কত পাঠিয়েছেন এবং TxID/Hash লিখে পাঠান:**\n\n"
            f"উদাহরণ: `20 USDT TRC20 - TxID: 8f92e1a04b`\n\n"
            f"📞 প্রয়োজনে যোগাযোগ করুন: {OWNER_USERNAME}",
            parse_mode="Markdown",
            reply_markup=get_bottom_menu_keyboard(state),
        )
        return

    if raw_text == BTN_FREE_DEPOSIT:
        state["menu_expanded"] = False
        push_navigation_view(state, "free_deposit_view")
        await update.message.reply_text(
            f"`{FREE_DEPOSIT_REQUEST_TEXT}`\n\n"
            f"👆 এই লেখাটি কপি করে সেন্ড করুন, সাথে সাথে **জয় (JOY)**-এর কাছে চলে যাবে এবং রিপ্লাই দিয়ে ফ্রি ডিপোজিট পাবেন।",
            parse_mode="Markdown",
            reply_markup=get_bottom_menu_keyboard(state),
        )
        return

    if not await is_user_joined(user.id, context):
        await update.message.reply_text(
            text=f"🔒 **আপনি চ্যানেলে জয়েন করেননি। আগে জয়েন করুন!**\n\nসমস্যা হলে যোগাযোগ: {OWNER_USERNAME}",
            parse_mode="Markdown",
            reply_markup=get_join_verify_keyboard(),
        )
        return

    market_btn_map = {
        BTN_30S: "30S",
        BTN_1M: "1M",
        BTN_3M: "3M",
        BTN_5M: "5M",
    }
    if raw_text in market_btn_map:
        await open_selected_market(market_btn_map[raw_text], update.message, user.first_name, state)
        return

    if raw_text == BTN_CHANGE_MARKET:
        state["market"] = None
        state["last_period"] = ""
        state["last_pred"] = None
        state["awaiting_deposit"] = False
        state["menu_expanded"] = True
        push_navigation_view(state, "market_menu")
        await send_market_prompt(update.message, user.first_name, state)
        return

    if raw_text == BTN_NEW_SIGNAL:
        market_key = state.get("market")
        if not isinstance(market_key, str) or market_key not in MARKETS:
            state["menu_expanded"] = True
            push_navigation_view(state, "market_menu")
            await send_market_prompt(update.message, user.first_name, state)
            return

        current_period, time_left = generate_market_period(market_key)
        prev_period = str(state.get("last_period") or "")
        prev_pred = state.get("last_pred")

        if prev_period and prev_period == current_period:
            await update.message.reply_text(
                f"⏳ পিরিয়ড `{current_period}` এখনো চলছে! নতুন সিগন্যালের জন্য আর **{time_left}s** অপেক্ষা করুন।",
                parse_mode="Markdown",
                reply_markup=get_bottom_menu_keyboard(state),
            )
            return

        if prev_period and prev_period != current_period and isinstance(prev_pred, str) and prev_pred in ("BIG", "SMALL"):
            result_msg = format_result_announcement(
                user_name=user.first_name,
                market_key=market_key,
                finished_period=prev_period,
                predicted_type=prev_pred,
            )
            await update.message.reply_text(text=result_msg, parse_mode="Markdown")

        card, pred_type = format_market_signal_card(
            user_name=user.first_name,
            market_key=market_key,
            period=current_period,
            time_left=time_left,
        )
        state["last_period"] = current_period
        state["last_pred"] = pred_type
        state["current_view"] = "signal_view"

        await update.message.reply_text(
            text=card,
            parse_mode="Markdown",
            reply_markup=get_bottom_menu_keyboard(state),
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
            state["current_view"] = "market_menu"
            state["nav_stack"] = []
            state["menu_expanded"] = False
            await query.answer("ভেরিফাই সফল! স্বাগতম ✅", show_alert=False)
            await send_market_prompt(query.message, user.first_name, state)
        else:
            await query.answer(
                f"আপনি এখনো চ্যানেলে জয়েন করেননি! আগে জয়েন করুন। সমস্যা হলে {OWNER_USERNAME} এ যোগাযোগ করুন।",
                show_alert=True,
            )


def main() -> None:
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("market", market_command))
    app.add_handler(CommandHandler("referral", referral_command))
    app.add_handler(CommandHandler("deposit", deposit_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))

    logger.info("OWNER OF JOY — জয় (JOY) VIP Signal Bot started...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
