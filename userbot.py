from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputVideoStream, InputAudioStream, InputStream
from flask import Flask, request
import asyncio
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = "user.session"
CHAT_ID = int(os.getenv("CHAT_ID"))  # معرف القناة أو الجروب

app_client = Client(SESSION, API_ID, API_HASH)
pytgcalls = PyTgCalls(app_client)
flask_app = Flask(__name__)

@flask_app.route("/start_broadcast", methods=["POST"])
def start_broadcast():
    data = request.json
    file_path = data.get("file")
    asyncio.create_task(broadcast(file_path))
    return "البث يبدأ…", 200

async def broadcast(file_path):
    await app_client.start()
    await pytgcalls.start()
    if file_path.endswith(".mp3"):
        pytgcalls.join_group_call(CHAT_ID, InputStream(InputAudioStream(file_path)))
    else:
        pytgcalls.join_group_call(
            CHAT_ID,
            InputStream(InputVideoStream(file_path), InputAudioStream(file_path))
        )
    print("البث بدأ!")

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=5000)
