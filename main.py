import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from yt_dlp import YoutubeDL

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("stream_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

@app.on_message(filters.command("play") & filters.group)
async def stream_video(client, message):

    if len(message.command) < 2:
        await message.reply_text("❗ الاستخدام: /play الرابط")
        return

    url = message.command[1]
    chat_id = message.chat.id

    os.makedirs("downloads", exist_ok=True)

    msg = await message.reply_text("🔄 جاري تحميل الفيديو...")

    try:
        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": f"downloads/{chat_id}.%(ext)s",
            "noplaylist": True,
            "quiet": True
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await msg.edit_text("🎥 جاري البث الآن...")

        await call_py.play(
            chat_id,
            MediaStream(file_path)
        )

    except Exception as e:
        await msg.edit_text(f"❌ خطأ: {e}")

@app.on_message(filters.command("stop") & filters.group)
async def stop_stream(client, message):
    try:
        await call_py.leave_call(message.chat.id)
        await message.reply_text("✅ تم إيقاف البث.")
    except:
        await message.reply_text("❌ لا يوجد بث حالياً.")

async def main():
    await app.start()
    await call_py.start()
    print("Bot Started Successfully")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

