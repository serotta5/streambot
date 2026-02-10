import os
import asyncio
from pyrogram import Client, filters
from yt_dlp import YoutubeDL

# جلب المتغيرات من إعدادات Railway
# لا تقم بتغيير هذه السطور، اتركها كما هي
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.text & filters.private)
async def handle_link(client, message):
    url = message.text
    
    # التحقق من أن النص يبدو كرابط
    if not url.startswith(("http", "www")):
        await message.reply_text("مرحباً! أرسل لي رابط فيديو (يوتيوب، تيك توك، فيسبوك...) وسأقوم بجلبه لك.")
        return

    status_msg = await message.reply_text("⏳ جاري التحميل والمعالجة... انتظر قليلاً")

    try:
        # إعدادات التحميل
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
        }

        # عملية التحميل
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            title = info.get('title', 'Video')

        # إرسال الفيديو
        await message.reply_video(
            video=file_path,
            caption=f"🎥 **{title}**",
            supports_streaming=True  # تفعيل خاصية المشاهدة الفورية
        )

        # تنظيف السيرفر
        os.remove(file_path)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ حدث خطأ أثناء جلب الفيديو.\nالسبب: {str(e)}")
        # محاولة حذف الملف في حال فشل الإرسال لتوفير المساحة
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

print("Bot Started Successfully!")
app.run()
