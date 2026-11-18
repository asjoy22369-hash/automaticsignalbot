import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from datetime import datetime
import pytz
import random

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# তোর API Token
TOKEN = "9064976363:AAF5y_IVLOQYFCkbsEGlKKR8ae3zKxu6Hsk"

# রিয়েল পিরিয়ড নাম্বার জেনারেটর (Wingo 30s)
def generate_wingo_period():
    bd_tz = pytz.timezone('Asia/Dhaka')
    now = datetime.now(bd_tz)
    date_str = now.strftime("%Y%m%d")
    total_seconds = now.hour * 3600 + now.minute * 60 + now.second
    period_index = (total_seconds // 30) + 1000
    return f"{date_str}100{period_index}"

# সিগন্যাল জেনারেটর (Action, Color, Number সহ)
def generate_signal_details():
    actions = [("BET BIG", "🔴 RED", "7"), ("BET SMALL", "🟢 GREEN", "2"), ("BET BIG", "🟢 GREEN", "9"), ("BET SMALL", "🔴 RED", "4")]
    action, color, number = random.choice(actions)
    return action, color, number

# /start কমান্ড (স্টার্ট লেখার সাথে সাথেই গর্জিয়াস স্টাইলে সব চলে আসবে)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    current_period = generate_wingo_period()
    action, color, number = generate_signal_details()
    
    welcome_text = (
        f"👑 **OWNER SAYEM & SIDDIK VIP SIGNAL** 👑\n"
        f"স্বাগতম, {user_name}! নিচে আপনার বর্তমান সিগন্যাল দেওয়া হলো:\n\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"💎 **𝐏𝐄𝐑𝐈𝐎𝐃** ➤ 📅 `{current_period}`\n"
        f"🎯 **𝐀𝐂𝐓𝐈𝐎𝐍** ➤ **{action}**\n"
        f"🎨 **𝐂𝐎𝐋𝐎𝐑** ➤ {color}\n"
        f"🔢 **𝐍𝐔𝐌𝐁𝐄𝐑** ➤ 💠  {number} \n"
        f"⚡ **𝐖𝐈𝐍𝐆𝐎** ➤ 𝟯𝟬𝗦 ⏱️\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"🔗 **𝗗𝗜𝗥𝗘𝗖𝗧 𝗪𝗘𝗕 𝗘𝗡𝗧𝗥𝗬**"
    )
    
    # ডিরেক্ট ওয়েব এন্ট্রি বাটন (লিংক তোর ইচ্ছমতো বসিয়ে নিতে পারবি)
    keyboard = [[InlineKeyboardButton("🌐 𝗖𝗟𝗜𝗖𝗞 𝗛𝗘𝗥𝗘 𝗧𝗢 𝗣𝗟𝗔𝗬", url="https://example.com")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

# /signal কমান্ড (আলাদা করে সিগন্যাল দেখার জন্য)
async def get_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_period = generate_wingo_period()
    action, color, number = generate_signal_details()
    
    signal_text = (
        f"👑 **SIDDIK VIP SIGNAL** 👑\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"💎 **𝐏𝐄𝐑𝐈𝐎𝐃** ➤ 📅 `{current_period}`\n"
        f"🎯 **𝐀𝐂𝐓𝐈𝐎𝐍** ➤ **{action}**\n"
        f"🎨 **𝐂𝐎𝐋𝐎𝐑** ➤ {color}\n"
        f"🔢 **𝐍𝐔𝐌𝐁𝐄𝐑** ➤ 💠  {number} \n"
        f"⚡ **𝐖𝐈𝐍𝐆Ο** ➤ 𝟯𝟬𝗦 ⏱️\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n"
        f"🔗 **𝗗𝗜𝗥𝗘𝗖𝗧 𝗪𝗘𝗕 𝗘𝗡𝗧𝗥𝗬**"
    )
    
    keyboard = [[InlineKeyboardButton("🌐 𝗖𝗟𝗜𝗖𝗞 𝗛𝗘𝗥𝗘 𝗧𝗢 𝗣𝗟𝗔𝗬", url="https://example.com")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(signal_text, parse_mode='Markdown', reply_markup=reply_markup)

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('signal', get_signal))

    print("Gorgeous Wingo Bot with Start & Signal is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
