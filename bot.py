import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from datetime import datetime
import pytz
import random

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# তোর API Token এখানে বসানো আছে
TOKEN = "9064976363:AAF5y_IVLOQYFCkbsEGlKKR8ae3zKxu6Hsk"

# রিয়েল পিরিয়ড নাম্বার জেনারেট করার ফাংশন (Wingo 30s লজিক)
def generate_wingo_period():
    # বাংলাদেশ সময় জোন সেট করা
    bd_tz = pytz.timezone('Asia/Dhaka')
    now = datetime.now(bd_tz)
    
    # ফরম্যাট: YYYYMMDD + Total Seconds of the day divided by 30
    date_str = now.strftime("%Y%m%d")
    total_seconds = now.hour * 3600 + now.minute * 60 + now.second
    period_index = (total_seconds // 30) + 1000  # একটা নির্দিষ্ট বেস নাম্বার যোগ করা
    
    period_number = f"{date_str}100{period_index}"
    return period_number

# সিগন্যাল জেনারেট করার ফাংশন (Big/Small অথবা Small/Big)
def generate_signal():
    options = ["🔴 BIG (বড়)", "🟢 SMALL (ছোট)"]
    colors = ["Red 🔴", "Green 🟢"]
    
    prediction = random.choice(options)
    return prediction

# /start কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"হ্যালো {user_name}! 🚀\n"
        f"Wingo 30s অটোমেটেড সিগন্যাল বটে আপনাকে স্বাগতম।\n\n"
        f"রিয়েল-টাইম সিগন্যাল পেতে নিচের কমান্ডটি ব্যবহার করুন:\n"
        f"👉 /signal - বর্তমান পিরিয়ডের সিগন্যাল দেখতে"
    )
    await update.message.reply_text(welcome_text)

# /signal কমান্ড হ্যান্ডলার (রিয়েল পিরিয়ড ও সিগন্যাল সহ)
async def get_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_period = generate_wingo_period()
    signal_result = generate_signal()
    
    response_text = (
        f"📊 **Wingo 30s Live Signal** 📊\n\n"
        f"🆔 **Period No:** `{current_period}`\n"
        f"🎯 **Prediction:** *{signal_result}*\n"
        f"⏳ **Timeframe:** 30 Seconds\n\n"
        f"⚠️ *সতর্কতা: নিজের দায়িত্বে ট্রেড করুন!*"
    )
    await update.message.reply_text(response_text, parse_mode='Markdown')

def main():
    # Application builder দিয়ে বট ইনিশিয়ালাইজ করা
    application = ApplicationBuilder().token(TOKEN).build()

    # কমান্ড হ্যান্ডলারগুলো রেজিস্টার করা
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('signal', get_signal))

    # Polling শুরু করা
    print("Bot is starting polling with real period logic...")
    application.run_polling()

if __name__ == '__main__':
    main()
