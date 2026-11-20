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

# তোর অফিসিয়াল রেফারেল লিংক
REFERRAL_PLATFORM_URL = "https://hgnice0.com/#/register?invitationCode=376851951983"

# হাইপারলিংক টেক্সটসমূহ (যাতে সরাসরি কাঁচা লিংক না দেখায়)
REFERRAL_HYPERLINK = f"[🔗 আমাদের লিংক থেকে অ্যাকাউন্ট করুন]({REFERRAL_PLATFORM_URL})"
CHANNEL_HYPERLINK = f"[📢 আমাদের টেলিগ্রাম চ্যানেলে জয়েন করুন]({CHANNEL_URL})"
SUPPORT_HYPERLINK = f"[💬 সমস্যা হলে যোগাযোগ করুন ({OWNER_USERNAME})]({OWNER_CONTACT_URL})"

# চ্যানেলেও অটো সিগন্যাল পাঠাতে চাইলে True রাখ, শুধু প্রাইভেট চ্যাটে ইউজারদের দিলে False রাখ
AUTO_BROADCAST_CHANNEL = False
BROADCAST_MARKET = "30S"

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
    f"📞 **Support:** {SUPPORT_HYPERLINK}"
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

# এন্ট্রি প্রশ্ন ও বাটন লেবেল
GATE_ANS_YES = "✅ হ্যাঁ"
GATE_ANS_NO = "❌ না"
GATE_ANS_DONE = "🔄 অ্যাকাউন্ট করেছি (আবার যাচাই করুন)"

# স্মার্ট কীবোর্ড বাটন লেবেলসমূহ
BTN_MENU_OPEN = "☰ মেনু"
BTN_MENU_CLOSE = "✕ মেনু বন্ধ"
BTN_AUTO_ON = "🤖 অটো সিগন্যাল চালু"
BTN_AUTO_OFF = "⏸️ অটো সিগন্যাল বন্ধ"
BTN_30S = "⚡ 30S"
BTN_1M = "⏱️ 1M"
BTN_3M = "🕒 3M"
BTN_5M = "🕔 5M"
BTN_NEW_SIGNAL = "🔄 নতুন সিগন্যাল নিন"
BTN_CHANGE_MARKET = "🔀 মার্কেট পরিবর্তন"
BTN_REFERRAL = "👥 রেফারেল সিস্টেম"
BTN_COIN_DEPOSIT = "🪙 কয়েনের মাধ্যমে ডিপোজিট করুন"
BTN_SUBMIT_DEPOSIT = "✍️ কয়েন ডিপোজিট তথ্য জমা দিন"
BTN_FREE_DEPOSIT = "🎁 ফ্রি ডিপোজিট নিন (10,000 কয়েন)"
BTN_SUPPORT = "💬 সাপোর্ট (@BDT588)"
BTN_BACK = "⬅️ Back"

# ইউজার স্টেট ট্র্যাক করার ডিকশনারি
user_states: dict[int, dict[str, object]] = {}

# চ্যানেল অটো ব্রডকাস্ট স্টেট
channel_auto_state: dict[str, object] = {
    "last_period": "",
    "last_pred": None,
}


def get_or_create_user(user_id: int, user_name: str, referred_by: int | None = None) -> dict[str, object]:
    state = user_states.get(user_id)
    if state is None:
        state = {
            "chat_id": user_id,
            "name": user_name,
            "market": None,
            "last_period": "",
            "last_pred": None,
            "auto_signal": True,
            "entry_verified": False,
            "entry_step": 1,
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
        state["chat_id"] = user_id
        state["name"] = user_name
        state.setdefault("auto_signal", True)
        state.setdefault("entry_verified", False)
        state.setdefault("entry_step", 1)
        state.setdefault("nav_stack", [])
        state.setdefault("current_view", "market_menu")
        state.setdefault("menu_expanded", False)
        if referred_by is not None and state.get("referred_by") is None and referred_by != user_id:
            state["referred_by"] = referred_by
    return state


def get_entry_keyboard(require_account_retry: bool = False) -> ReplyKeyboardMarkup:
    if require_account_retry:
        rows = [
            [KeyboardButton(GATE_ANS_DONE)],
            [KeyboardButton(GATE_ANS_YES), KeyboardButton(GATE_ANS_NO)],
        ]
    else:
        rows = [[KeyboardButton(GATE_ANS_YES), KeyboardButton(GATE_ANS_NO)]]
    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="উত্তর দিতে 'হ্যাঁ' অথবা 'না' বাটনে চাপুন...",
    )


async def send_entry_step_prompt(message_obj, user_name: str, step: int, retry_mode: bool = False) -> None:
    if step == 1:
        if retry_mode:
            text = (
                f"⚠️ **যদি না করে থাকেন তাহলে নিচের লিংক থেকে অ্যাকাউন্ট করে নিন:**\n\n"
                f"👉 {REFERRAL_HYPERLINK}\n"
                f"👉 {CHANNEL_HYPERLINK}\n"
                f"👉 {SUPPORT_HYPERLINK}\n\n"
                f"অ্যাকাউন্ট করা হয়ে গেলে নিচের বাটনে চাপুন:"
            )
            await message_obj.reply_text(
                text=text,
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=get_entry_keyboard(require_account_retry=True),
            )
            return

        text = (
            f"{BOT_TOP_DESCRIPTION}\n"
            f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
            f"স্বাগতম **{user_name}**! 🌟\n\n"
            f"**প্রশ্ন ১/৩:** আপনি কি আমাদের লিংক থেকে অ্যাকাউন্ট করছেন?\n"
            f"*(যদি না করে থাকেন তাহলে নিচের লেখাটিতে ক্লিক করে অ্যাকাউন্ট করে নিন)*\n\n"
            f"👉 {REFERRAL_HYPERLINK}\n"
            f"👉 {CHANNEL_HYPERLINK}\n"
            f"👉 {SUPPORT_HYPERLINK}"
        )
        await message_obj.reply_text(
            text=text,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=get_entry_keyboard(require_account_retry=False),
        )
        return

    if step == 2:
        text = (
            f"**প্রশ্ন ২/৩:** আপনি কি শান্ত মাথায়, ধৈর্য ও নিয়ম মেনে ট্রেড করতে প্রস্তুত?\n"
            f"*(তাড়াহুড়ো বা আবেগ নয়—শৃঙ্খলাই সাফল্যের মূল ভিত্তি)*"
        )
        await message_obj.reply_text(
            text=text,
            parse_mode="Markdown",
            reply_markup=get_entry_keyboard(require_account_retry=False),
        )
        return

    text = (
        f"**প্রশ্ন ৩/৩:** আপনি কি **OWNER OF JOY — জয় (JOY)**-এর নিয়মকানুন ও সিগন্যাল গাইডলাইন মেনে চলতে রাজি?"
    )
    await message_obj.reply_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=get_entry_keyboard(require_account_retry=False),
    )


async def handle_entry_gate_response(
    raw_text: str,
    message_obj,
    user_name: str,
    state: dict[str, object],
) -> bool:
    if bool(state.get("entry_verified", False)):
        return False

    step = int(state.get("entry_step", 1) or 1)

    if raw_text not in (GATE_ANS_YES, GATE_ANS_NO, GATE_ANS_DONE):
        await send_entry_step_prompt(
            message_obj,
            user_name,
            step=step,
            retry_mode=(step == 1 and raw_text != GATE_ANS_YES),
        )
        return True

    if step == 1:
        if raw_text == GATE_ANS_NO:
            await message_obj.reply_text(
                f"❌ **যদি না করে থাকেন তাহলে নিচের লিংক থেকে অ্যাকাউন্ট করে নিন:**\n\n"
                f"👉 {REFERRAL_HYPERLINK}\n"
                f"👉 {CHANNEL_HYPERLINK}\n"
                f"👉 {SUPPORT_HYPERLINK}\n\n"
                f"অ্যাকাউন্ট করার পর **{GATE_ANS_DONE}** অথবা **{GATE_ANS_YES}** চাপুন।",
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=get_entry_keyboard(require_account_retry=True),
            )
            return True

        if raw_text == GATE_ANS_DONE:
            state["entry_step"] = 2
            await message_obj.reply_text(
                "✅ ধন্যবাদ! অ্যাকাউন্ট নিশ্চিতকরণ গ্রহণ করা হয়েছে।",
                parse_mode="Markdown",
            )
            await send_entry_step_prompt(message_obj, user_name, step=2)
            return True

        # GATE_ANS_YES
        state["entry_step"] = 2
        await send_entry_step_prompt(message_obj, user_name, step=2)
        return True

    if step == 2:
        if raw_text == GATE_ANS_NO:
            await message_obj.reply_text(
                f"⚠️ ট্রেডিংয়ে সফল হতে হলে ধৈর্য ও শৃঙ্খলা জরুরি। প্রস্তুত হলে **{GATE_ANS_YES}** চাপুন।",
                parse_mode="Markdown",
                reply_markup=get_entry_keyboard(require_account_retry=False),
            )
            return True

        state["entry_step"] = 3
        await send_entry_step_prompt(message_obj, user_name, step=3)
        return True

    # step == 3
    if raw_text == GATE_ANS_NO:
        await message_obj.reply_text(
            f"⚠️ সিস্টেমে প্রবেশ করতে নিয়মকানুন মেনে নিতে হবে। রাজি থাকলে **{GATE_ANS_YES}** চাপুন।",
            parse_mode="Markdown",
            reply_markup=get_entry_keyboard(require_account_retry=False),
        )
        return True

    state["entry_verified"] = True
    state["entry_step"] = 3
    state["market"] = None
    state["last_period"] = ""
    state["last_pred"] = None
    state["auto_signal"] = True
    state["current_view"] = "market_menu"
    state["nav_stack"] = []
    state["menu_expanded"] = False

    await message_obj.reply_text(
        "🎉 **অভিনন্দন! সবগুলো প্রশ্নের উত্তর সফলভাবে সম্পন্ন হয়েছে—এখন আপনি বটে এন্ট্রি নিতে পারবেন!**",
        parse_mode="Markdown",
    )
    await send_market_prompt(message_obj, user_name, state)
    return True


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
        f"🤖 *Mode:* **AUTO LIVE** • {SUPPORT_HYPERLINK}"
    )
    return card, pred_type


async def build_referral_message(user_id: int, user_name: str, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot_info = await context.bot.get_me()
    bot_username = bot_info.username or "YourBotUsername"
    bot_ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"

    state = get_or_create_user(user_id, user_name)
    refs = state.get("referrals", [])
    ref_count = len(refs) if isinstance(refs, list) else 0
    coins = int(state.get("referral_bonus", 0) or 0)
    claimed = int(state.get("free_deposits_claimed", 0) or 0)

    return (
        f"👥 **রেফারেল সিস্টেম — জয় (JOY)** 👥\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"👤 *Member:* `{user_name}`\n"
        f"🔗 *আপনার বট রেফারেল লিংক:* [👥 বন্ধুদের ইনভাইট করতে ক্লিক করুন]({bot_ref_link})\n"
        f"🌐 *অফিসিয়াল রেজিস্ট্রেশন:* {REFERRAL_HYPERLINK}\n\n"
        f"📊 *মোট রেফারেল:* **{ref_count} জন**\n"
        f"🪙 *বর্তমান কয়েন ব্যালেন্স:* **{coins:,} কয়েন**\n"
        f"✨ *প্রতি ১টি রেফারে পাবেন:* **{REFERRAL_BONUS_PER_USER} কয়েন**\n"
        f"🎁 *ফ্রি ডিপোজিট টার্গেট:* **{FREE_DEPOSIT_TARGET_COINS:,} কয়েন**\n"
        f"🆓 *নেওয়া ফ্রি ডিপোজিট:* **{claimed}টি**\n\n"
        f"👉 {CHANNEL_HYPERLINK}\n"
        f"👉 {SUPPORT_HYPERLINK}"
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
        f"👉 {SUPPORT_HYPERLINK}"
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
        [InlineKeyboardButton("🔗 অফিসিয়াল অ্যাকাউন্ট তৈরি করুন", url=REFERRAL_PLATFORM_URL)],
        [InlineKeyboardButton("✅ জয়েন ভেরিফাই করুন", callback_data="verify_join")],
        [InlineKeyboardButton("💬 যোগাযোগ (@BDT588)", url=OWNER_CONTACT_URL)],
    ])


def get_bottom_menu_keyboard(state: dict[str, object]) -> ReplyKeyboardMarkup:
    view_name = str(state.get("current_view") or "market_menu")
    menu_expanded = bool(state.get("menu_expanded", False))
    auto_on = bool(state.get("auto_signal", True))
    stack = state.get("nav_stack", [])
    has_prev = isinstance(stack, list) and len(stack) > 0
    auto_btn = BTN_AUTO_OFF if auto_on else BTN_AUTO_ON

    if not menu_expanded:
        top_row = [KeyboardButton(auto_btn), KeyboardButton(BTN_MENU_OPEN)]
        rows = [top_row]
        if has_prev:
            rows.append([KeyboardButton(BTN_BACK)])
        return ReplyKeyboardMarkup(
            rows,
            resize_keyboard=True,
            is_persistent=True,
            input_field_placeholder="🤖 অটো সিগন্যাল সক্রিয় • ☰ মেনু চাপুন...",
        )

    if view_name == "signal_view":
        rows = [
            [KeyboardButton(BTN_30S), KeyboardButton(BTN_1M), KeyboardButton(BTN_3M), KeyboardButton(BTN_5M)],
            [KeyboardButton(auto_btn), KeyboardButton(BTN_NEW_SIGNAL)],
            [KeyboardButton(BTN_CHANGE_MARKET), KeyboardButton(BTN_COIN_DEPOSIT)],
            [KeyboardButton(BTN_REFERRAL), KeyboardButton(BTN_SUPPORT)],
        ]
    elif view_name in ("deposit_view", "referral_view"):
        rows = [
            [KeyboardButton(BTN_SUBMIT_DEPOSIT), KeyboardButton(BTN_FREE_DEPOSIT)],
            [KeyboardButton(BTN_30S), KeyboardButton(BTN_1M), KeyboardButton(BTN_3M), KeyboardButton(BTN_5M)],
            [KeyboardButton(BTN_REFERRAL), KeyboardButton(BTN_COIN_DEPOSIT)],
            [KeyboardButton(auto_btn), KeyboardButton(BTN_SUPPORT)],
        ]
    else:
        rows = [
            [KeyboardButton(BTN_30S), KeyboardButton(BTN_1M), KeyboardButton(BTN_3M), KeyboardButton(BTN_5M)],
            [KeyboardButton(BTN_COIN_DEPOSIT), KeyboardButton(BTN_REFERRAL)],
            [KeyboardButton(auto_btn), KeyboardButton(BTN_SUPPORT)],
        ]

    control_row = [KeyboardButton(BTN_MENU_CLOSE)]
    if has_prev:
        control_row.append(KeyboardButton(BTN_BACK))
    rows.append(control_row)

    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="অপশন বেছে নিন অথবা ✕ মেনু বন্ধ চাপুন...",
    )


async def send_market_prompt(message_obj, user_name: str, state: dict[str, object]) -> None:
    auto_status = "চালু (AUTO)" if bool(state.get("auto_signal", True)) else "বন্ধ (OFF)"
    text = (
        f"{BOT_TOP_DESCRIPTION}\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"স্বাগতম **{user_name}**! 🌟\n"
        f"🤖 **Auto Signal Mode:** **{auto_status}**\n"
        f"আপনি কয় সেকেন্ডে ট্রেড করতে চান? আপনি ১ মিনিটে (`1M`) না ৩০ সেকেন্ডে (`30S`)—অপশন চালু করতে নিচের `{BTN_MENU_OPEN}` বাটনে ক্লিক করুন:\n\n"
        f"👉 {CHANNEL_HYPERLINK} • {SUPPORT_HYPERLINK}"
    )
    await message_obj.reply_text(
        text=text,
        parse_mode="Markdown",
        disable_web_page_preview=True,
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
            disable_web_page_preview=True,
            reply_markup=get_bottom_menu_keyboard(state),
        )
        return

    if view_name == "deposit_view":
        msg = build_coin_deposit_message(user_id, user_name)
        await message_obj.reply_text(
            msg,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=get_bottom_menu_keyboard(state),
        )
        return

    if view_name == "submit_deposit_view":
        state["awaiting_deposit"] = True
        await message_obj.reply_text(
            f"✍️ **আপনি কোন কয়েনে কত পাঠিয়েছেন এবং TxID/Hash লিখে পাঠান:**\n\n"
            f"উদাহরণ: `20 USDT TRC20 - TxID: 8f92e1a04b`\n\n"
            f"👉 {SUPPORT_HYPERLINK}",
            parse_mode="Markdown",
            disable_web_page_preview=True,
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
                disable_web_page_preview=True,
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
    state["auto_signal"] = True
    state["menu_expanded"] = False
    push_navigation_view(state, "signal_view")

    await message_obj.reply_text(
        text=card,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=get_bottom_menu_keyboard(state),
    )


async def auto_signal_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    for _, state in list(user_states.items()):
        if not bool(state.get("auto_signal", True)):
            continue
        if not bool(state.get("entry_verified", False)):
            continue

        market_key = state.get("market")
        chat_id = state.get("chat_id")
        user_name = str(state.get("name") or "Trader")
        if not isinstance(market_key, str) or market_key not in MARKETS or not isinstance(chat_id, int):
            continue

        current_period, time_left = generate_market_period(market_key)
        prev_period = str(state.get("last_period") or "")
        prev_pred = state.get("last_pred")

        if prev_period and prev_period != current_period:
            try:
                if isinstance(prev_pred, str) and prev_pred in ("BIG", "SMALL"):
                    result_msg = format_result_announcement(
                        user_name=user_name,
                        market_key=market_key,
                        finished_period=prev_period,
                        predicted_type=prev_pred,
                    )
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=result_msg,
                        parse_mode="Markdown",
                    )

                card, pred_type = format_market_signal_card(
                    user_name=user_name,
                    market_key=market_key,
                    period=current_period,
                    time_left=time_left,
                )
                state["last_period"] = current_period
                state["last_pred"] = pred_type
                state["current_view"] = "signal_view"

                await context.bot.send_message(
                    chat_id=chat_id,
                    text=card,
                    parse_mode="Markdown",
                    disable_web_page_preview=True,
                    reply_markup=get_bottom_menu_keyboard(state),
                )
            except Exception as e:
                logger.error(f"Auto signal push failed for user {chat_id}: {e}")

    if AUTO_BROADCAST_CHANNEL and BROADCAST_MARKET in MARKETS:
        current_period, time_left = generate_market_period(BROADCAST_MARKET)
        prev_period = str(channel_auto_state.get("last_period") or "")
        prev_pred = channel_auto_state.get("last_pred")

        if not prev_period:
            card, pred_type = format_market_signal_card(
                user_name="DK WIN • HGNICE VIP",
                market_key=BROADCAST_MARKET,
                period=current_period,
                time_left=time_left,
            )
            channel_auto_state["last_period"] = current_period
            channel_auto_state["last_pred"] = pred_type
            try:
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=card,
                    parse_mode="Markdown",
                    disable_web_page_preview=True,
                )
            except Exception as e:
                logger.error(f"Channel initial auto signal failed: {e}")
        elif prev_period != current_period:
            try:
                if isinstance(prev_pred, str) and prev_pred in ("BIG", "SMALL"):
                    result_msg = format_result_announcement(
                        user_name="DK WIN • HGNICE VIP",
                        market_key=BROADCAST_MARKET,
                        finished_period=prev_period,
                        predicted_type=prev_pred,
                    )
                    await context.bot.send_message(chat_id=CHANNEL_ID, text=result_msg, parse_mode="Markdown")

                card, pred_type = format_market_signal_card(
                    user_name="DK WIN • HGNICE VIP",
                    market_key=BROADCAST_MARKET,
                    period=current_period,
                    time_left=time_left,
                )
                channel_auto_state["last_period"] = current_period
                channel_auto_state["last_pred"] = pred_type
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=card,
                    parse_mode="Markdown",
                    disable_web_page_preview=True,
                )
            except Exception as e:
                logger.error(f"Channel auto signal update failed: {e}")


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
            f"👉 {CHANNEL_HYPERLINK}\n"
            f"👉 {REFERRAL_HYPERLINK}\n"
            f"👉 {SUPPORT_HYPERLINK}\n\n"
            f"নিচের বাটনে ক্লিক করে চ্যানেলে জয়েন করুন, তারপর **✅ জয়েন ভেরিফাই করুন** চাপুন।",
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=get_join_verify_keyboard(),
        )
        return

    state["entry_verified"] = False
    state["entry_step"] = 1
    state["market"] = None
    state["last_period"] = ""
    state["last_pred"] = None
    state["auto_signal"] = True
    state["awaiting_deposit"] = False
    state["current_view"] = "market_menu"
    state["nav_stack"] = []
    state["menu_expanded"] = False
    await send_entry_step_prompt(update.message, user.first_name, step=1)


async def market_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.message:
        return

    state = get_or_create_user(user.id, user.first_name)
    if not bool(state.get("entry_verified", False)):
        await send_entry_step_prompt(
            update.message,
            user.first_name,
            step=int(state.get("entry_step", 1) or 1),
        )
        return

    if not await is_user_joined(user.id, context):
        await update.message.reply_text(
            f"{BOT_TOP_DESCRIPTION}\n"
            f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
            f"🔒 **আগে টেলিগ্রাম চ্যানেলে জয়েন করুন!**\n👉 {CHANNEL_HYPERLINK}",
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=get_join_verify_keyboard(),
        )
        return

    state["menu_expanded"] = True
    push_navigation_view(state, "market_menu")
    await send_market_prompt(update.message, user.first_name, state)


async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.message:
        return

    state = get_or_create_user(user.id, user.first_name)
    if not bool(state.get("entry_verified", False)):
        await send_entry_step_prompt(
            update.message,
            user.first_name,
            step=int(state.get("entry_step", 1) or 1),
        )
        return

    push_navigation_view(state, "referral_view")
    msg = await build_referral_message(user.id, user.first_name, context)
    await update.message.reply_text(
        msg,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=get_bottom_menu_keyboard(state),
    )


async def deposit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.message:
        return

    state = get_or_create_user(user.id, user.first_name)
    if not bool(state.get("entry_verified", False)):
        await send_entry_step_prompt(
            update.message,
            user.first_name,
            step=int(state.get("entry_step", 1) or 1),
        )
        return

    push_navigation_view(state, "deposit_view")
    msg = build_coin_deposit_message(user.id, user.first_name)
    await update.message.reply_text(
        msg,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=get_bottom_menu_keyboard(state),
    )


async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.message or not update.message.text:
        return

    raw_text = update.message.text.strip()
    state = get_or_create_user(user.id, user.first_name)

    if not bool(state.get("entry_verified", False)):
        await handle_entry_gate_response(raw_text, update.message, user.first_name, state)
        return

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
            f"👉 {SUPPORT_HYPERLINK}",
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=get_bottom_menu_keyboard(state),
        )
        return

    if bool(state.get("awaiting_deposit", False)) and raw_text not in {
        BTN_MENU_OPEN,
        BTN_MENU_CLOSE,
        BTN_AUTO_ON,
        BTN_AUTO_OFF,
        BTN_BACK,
        BTN_CHANGE_MARKET,
        BTN_REFERRAL,
        BTN_COIN_DEPOSIT,
        BTN_FREE_DEPOSIT,
        BTN_NEW_SIGNAL,
        BTN_SUPPORT,
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
            f"👉 {SUPPORT_HYPERLINK}"
        )
        await update.message.reply_text(
            confirm_text,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=get_bottom_menu_keyboard(state),
        )
        return

    if raw_text == BTN_SUPPORT:
        await update.message.reply_text(
            f"💬 **সাপোর্ট ও সরাসরি যোগাযোগ — জয় (JOY)**\n\n"
            f"👉 {SUPPORT_HYPERLINK}\n"
            f"👉 {CHANNEL_HYPERLINK}\n"
            f"👉 {REFERRAL_HYPERLINK}",
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=get_bottom_menu_keyboard(state),
        )
        return

    if raw_text == BTN_AUTO_ON:
        state["auto_signal"] = True
        market_key = state.get("market")
        if not isinstance(market_key, str) or market_key not in MARKETS:
            state["market"] = "30S"
            market_key = "30S"

        period, time_left = generate_market_period(market_key)
        card, pred_type = format_market_signal_card(user.first_name, market_key, period, time_left)
        state["last_period"] = period
        state["last_pred"] = pred_type
        state["current_view"] = "signal_view"

        await update.message.reply_text(
            f"🤖 **অটো সিগন্যাল মোড চালু হয়েছে!** ({MARKETS[market_key][0]})\nপ্রতি পিরিয়ড শেষ হলেই অটোমেটিক নতুন সিগন্যাল চলে আসবে।",
            parse_mode="Markdown",
            reply_markup=get_bottom_menu_keyboard(state),
        )
        await update.message.reply_text(
            text=card,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=get_bottom_menu_keyboard(state),
        )
        return

    if raw_text == BTN_AUTO_OFF:
        state["auto_signal"] = False
        await update.message.reply_text(
            f"⏸️ **অটো সিগন্যাল মোড সাময়িক বন্ধ করা হয়েছে।** আবার চালু করতে `{BTN_AUTO_ON}` চাপুন।",
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
            disable_web_page_preview=True,
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
            disable_web_page_preview=True,
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
            f"👉 {SUPPORT_HYPERLINK}",
            parse_mode="Markdown",
            disable_web_page_preview=True,
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
            text=f"🔒 **আপনি চ্যানেলে জয়েন করেননি। আগে জয়েন করুন!**\n\n👉 {CHANNEL_HYPERLINK}\n👉 {SUPPORT_HYPERLINK}",
            parse_mode="Markdown",
            disable_web_page_preview=True,
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
            disable_web_page_preview=True,
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
            state["entry_verified"] = False
            state["entry_step"] = 1
            state["market"] = None
            state["last_period"] = ""
            state["last_pred"] = None
            state["auto_signal"] = True
            state["current_view"] = "market_menu"
            state["nav_stack"] = []
            state["menu_expanded"] = False
            await query.answer("চ্যানেল ভেরিফাই সফল! এবার ৩টি প্রশ্ন সম্পন্ন করুন ✅", show_alert=False)
            await send_entry_step_prompt(query.message, user.first_name, step=1)
        else:
            await query.answer(
                f"আপনি এখনো চ্যানেলে জয়েন করেননি! আগে জয়েন করুন। সমস্যা হলে {OWNER_USERNAME} এ যোগাযোগ করুন।",
                show_alert=True,
            )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)


def main() -> None:
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("market", market_command))
    app.add_handler(CommandHandler("referral", referral_command))
    app.add_handler(CommandHandler("deposit", deposit_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    app.add_error_handler(error_handler)

    if app.job_queue is not None:
        app.job_queue.run_repeating(auto_signal_tick, interval=1, first=2)

    logger.info("OWNER OF JOY — জয় (JOY) VIP Signal Bot with Hyperlinked Onboarding started...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
