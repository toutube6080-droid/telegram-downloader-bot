from aiogram import Bot, Dispatcher, executor, types
import yt_dlp
import os

BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"

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

    except Exception:
        await message.reply("❌ Failed. Send a valid public link.")

if __name__ == "__main__":
    executor.start_polling(dp)
