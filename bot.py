import asyncio
import datetime
import logging
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# তোর টোকেন এখানে বসানো আছে
TOKEN = "9064976363:AAF5y_IVLOQYFCkbsEGlKKR8ae3zKxu6Hsk"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

user_signals = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  keyboard = [[InlineKeyboardButton("🟢 Wingo 30s Market", callback_data="wingo_30s")]]
  reply_markup = InlineKeyboardMarkup(keyboard)

  welcome_text = (
      "👑 **স্বাগতম উইনগো সিগন্যাল বোটে!**\n\n"
      "নিচের বাটন থেকে মার্কেট সিলেক্ট করে অটোমেটিক সিগন্যাল পাওয়া শুরু করো।"
  )
  await update.message.reply_text(
      welcome_text, reply_markup=reply_markup, parse_mode="Markdown"
  )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()
  user_id = query.from_user.id

  if query.data == "wingo_30s":
    if user_signals.get(user_id):
      await query.edit_message_text(
          "⚠️ তোমার সিগন্যাল অলরেডি রানিং আছে!"
      )
      return

    user_signals[user_id] = True
    keyboard = [
        [InlineKeyboardButton("❌ সিগন্যাল বন্ধ করো", callback_data="stop_signal")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "🚀 **Wingo 30s** মার্কেট সিগন্যাল শুরু হয়েছে!\nপ্রতি ৩০ সেকেন্ড পরপর আপডেট আসবে।",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )

    while user_signals.get(user_id, False):
      try:
        now = datetime.datetime.now()
        period_no = (
            now.strftime("%Y%m%d")
            + "100"
            + str(now.hour * 3600 + now.minute * 60 + now.second // 30)
        )

        signal_result = random.choice(["🟢 BIG", "🔴 SMALL"])

        signal_msg = (
            f"📊 **Wingo 30s Signal**\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🔢 **Period No:** `{period_no}`\n"
            f"🎯 **Prediction:** {signal_result}\n"
            f"⏳ **Time:** {now.strftime('%H:%M:%S')}\n"
            f"━━━━━━━━━━━━━━━━━━━"
        )

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=signal_msg,
            parse_mode="Markdown",
        )

        await asyncio.sleep(30)
      except Exception as e:
        logging.error(f"Error in signal loop: {e}")
        break

  elif query.data == "stop_signal":
    user_signals[user_id] = False
    keyboard = [[InlineKeyboardButton("🟢 Wingo 30s Market", callback_data="wingo_30s")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "⏹️ সিগন্যাল বন্ধ করা হয়েছে। পুনরায় শুরু করতে চাইলে নিচের বাটনে ক্লিক করো:",
        reply_markup=reply_markup,
    )


def main():
  app = ApplicationBuilder().token(TOKEN).build()
  app.add_handler(CommandHandler("start", start))
  app.add_handler(CallbackQueryHandler(button))

  print("🤖 বট সফলভাবে চালু হয়েছে এবং কাজ করছে...")
  app.run_polling()


if __name__ == "__main__":
  main()
