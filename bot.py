from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import os
import re
import yt_dlp

TOKEN = 'ضع_توكن_البوت_هنا'

# مجلدات مؤقتة لتخزين الملفات
os.makedirs("temp_videos", exist_ok=True)
os.makedirs("temp_mp3", exist_ok=True)

user_choice = {}
user_files = {}

YOUTUBE_REGEX = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"

# --- /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎥 فيديو", callback_data="video")],
        [InlineKeyboardButton("🎵 MP3", callback_data="mp3")],
        [InlineKeyboardButton("▶️ ابدأ البث", callback_data="start_broadcast")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر نوع الملف أو ابدأ البث:", reply_markup=reply_markup)

# --- التعامل مع أزرار ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_choice[query.from_user.id] = query.data

    if query.data in ["video", "mp3"]:
        await query.message.reply_text(f"أرسل لي {query.data} الآن أو رابط يوتيوب إذا اخترت فيديو")
    elif query.data == "start_broadcast":
        file_path = user_files.get(query.from_user.id)
        if file_path:
            await update.message.reply_text("تم تجهيز الملف للبث! يمكنك الآن البث من Userbot أو PyTgCalls.")
        else:
            await update.message.reply_text("لم يتم رفع أي ملف بعد.")

# --- التعامل مع الرسائل ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    choice = user_choice.get(user_id)
    if not choice:
        await update.message.reply_text("اضغط على /start لاختيار نوع الملف أولاً")
        return

    text = update.message.text or ""

    # روابط يوتيوب
    if choice == "video" and re.search(YOUTUBE_REGEX, text):
        await update.message.reply_text("جارٍ تحميل الفيديو من يوتيوب…")
        try:
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': f'temp_videos/%(id)s.%(ext)s',
                'noplaylist': True,
                'quiet': True,
                'merge_output_format': 'mp4'
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                file_path = ydl.prepare_filename(info)
                user_files[user_id] = file_path
            await update.message.reply_text(f"تم حفظ الفيديو من يوتيوب: {file_path}")
        except Exception as e:
            await update.message.reply_text(f"فشل تحميل الفيديو: {e}")
        return

    # ملفات الفيديو أو MP3
    file = None
    path = None
    if choice == "video" and (update.message.video or (update.message.document and update.message.document.mime_type.startswith("video/"))):
        file = update.message.video or update.message.document
        path = f"temp_videos/{file.file_unique_id}.mp4"
    elif choice == "mp3" and (update.message.audio or (update.message.document and update.message.document.mime_type == "audio/mpeg")):
        file = update.message.audio or update.message.document
        path = f"temp_mp3/{file.file_unique_id}.mp3"

    if file and path:
        tfile = await file.get_file()
        await tfile.download_to_drive(path)
        user_files[user_id] = path
        await update.message.reply_text(f"تم حفظ الملف: {path}")
    else:
        await update.message.reply_text("أرسل الملف الصحيح أو رابط يوتيوب إذا اخترت فيديو")

# --- بدء البوت ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    print("البوت يعمل الآن…")
    app.run_polling()
