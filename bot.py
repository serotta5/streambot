from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import os
import requests  # لإرسال طلب HTTP للـ Userbot

TOKEN = os.getenv("BOT_TOKEN")
os.makedirs("videos", exist_ok=True)
os.makedirs("mp3", exist_ok=True)

user_choice = {}  # يخزن اختيار كل مستخدم
user_files = {}   # يخزن مسار الملف لكل مستخدم

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎥 فيديو", callback_data="video")],
        [InlineKeyboardButton("🎵 MP3", callback_data="mp3")],
        [InlineKeyboardButton("🔗 رابط", callback_data="link")],
        [InlineKeyboardButton("▶️ ابدأ البث", callback_data="start_broadcast")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر نوع الإدخال أو ابدأ البث:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_choice[query.from_user.id] = query.data

    if query.data in ["video", "mp3", "link"]:
        await query.message.reply_text(f"أرسل لي {query.data} الآن")
    elif query.data == "start_broadcast":
        file_path = user_files.get(query.from_user.id)
        if file_path:
            # إرسال طلب للبث للـ Userbot
            requests.post("http://127.0.0.1:5000/start_broadcast", json={"file": file_path})
            await query.message.reply_text("تم إرسال طلب البث للـ Userbot…")
        else:
            await query.message.reply_text("لم يتم رفع أي ملف للبث بعد.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    choice = user_choice.get(user_id)
    if not choice:
        await update.message.reply_text("اضغط على /start لاختيار نوع الإدخال أولاً")
        return

    if choice == "video" and update.message.video:
        file = await update.message.video.get_file()
        path = f"./videos/{file.file_unique_id}.mp4"
        await file.download_to_drive(path)
        user_files[user_id] = path
        await update.message.reply_text(f"تم حفظ الفيديو: {path}")

    elif choice == "mp3" and update.message.audio:
        file = await update.message.audio.get_file()
        path = f"./mp3/{file.file_unique_id}.mp3"
        await file.download_to_drive(path)
        user_files[user_id] = path
        await update.message.reply_text(f"تم حفظ MP3: {path}")

    elif choice == "link" and update.message.text:
        user_files[user_id] = update.message.text
        await update.message.reply_text(f"تم حفظ الرابط: {update.message.text}")

    else:
        await update.message.reply_text("الرجاء إرسال النوع الصحيح من الملف")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    print("البوت يعمل الآن…")
    app.run_polling()
