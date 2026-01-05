from aiogram import Bot, Dispatcher, executor, types
import yt_dlp
import os
import threading
from flask import Flask

# ===== KEEP RENDER ALIVE =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive"

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()
# ============================

BOT_TOKEN = os.getenv("BOT_TOKEN") or "8304098491:AAFzuQnfAS3dy3bnjIh0IG8vP3bsNHChj5A"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply(
        "📥 Send YouTube / Instagram / Pinterest link\n"
        "⚠️ Only public videos"
    )

@dp.message_handler()
async def download(message: types.Message):
    url = message.text
    await message.reply("⏳ Downloading...")

    ydl_opts = {
        'format': 'mp4',
        'outtmpl': 'video.%(ext)s'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open("video.mp4", "rb") as video:
            await message.reply_video(video)

        os.remove("video.mp4")

    except Exception as e:
        await message.reply("❌ Failed. Send a valid public link.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
