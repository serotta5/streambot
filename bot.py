from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import os

# التوكن كمتغير بيئة (آمن لـ Railway)
TOKEN = os.getenv("BOT_TOKEN")

# إنشاء مجلد لتخزين الفيديوهات
os.makedirs("videos", exist_ok=True)

# تخزين اختيار المستخدم (فيديو أم رابط)
user_choice = {}

# أمر البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎥 فيديو", callback_data="video")],
        [InlineKeyboardButton("🔗 رابط", callback_data="link")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("مرحبًا! اختر نوع الإدخال:", reply_markup=reply_markup)

# التعامل مع ضغط الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_choice[query.from_user.id] = query.data
    if query.data == "video":
        await query.message.reply_text("أرسل لي الفيديو الآن")
    elif query.data == "link":
        await query.message.reply_text("أرسل لي الرابط الآن")

# التعامل مع الرسائل (فيديو أو رابط)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_choice:
        await update.message.reply_text("اضغط على /start لاختيار نوع الإدخال أولاً")
        return

    choice = user_choice[user_id]

    if choice == "video" and update.message.video:
        file = await update.message.video.get_file()
        path = f"./videos/{file.file_unique_id}.mp4"
        await file.download_to_drive(path)
        await update.message.reply_text(f"تم حفظ الفيديو: {path}\nجاهز للبث لاحقًا!")
    elif choice == "link" and update.message.text:
        await update.message.reply_text(f"تم استلام الرابط: {update.message.text}\nجاهز للبث لاحقًا!")
    else:
        await update.message.reply_text("الرجاء إرسال نوع الملف الصحيح")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    print("البوت يعمل الآن...")
    app.run_polling()
