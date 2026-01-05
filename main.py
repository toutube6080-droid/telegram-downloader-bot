from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import yt_dlp
import os
import threading
from flask import Flask

# ===== Keep Render alive =====
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

user_links = {}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("📥 Send Instagram or Pinterest link")

@dp.message_handler()
async def get_link(message: types.Message):
    url = message.text

    if "youtube.com" in url or "youtu.be" in url:
        await message.reply("❌ YouTube is not supported on cloud servers.")
        return

    user_links[message.from_user.id] = url

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🎥 Video", callback_data="video"),
        InlineKeyboardButton("🎵 Audio", callback_data="audio")
    )

    await message.reply("What do you want to download?", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data in ["video", "audio"])
async def process_choice(callback_query: types.CallbackQuery):
    choice = callback_query.data
    user_id = callback_query.from_user.id
    url = user_links.get(user_id)

    if not url:
        await callback_query.message.reply("❌ Link expired. Send again.")
        return

    await callback_query.message.edit_text("⏳ Processing...")

    try:
        caption_text = "Downloaded by Nero Bot\nhttps://t.me/YourBotUsername"

if choice == "video":
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    with open("video.mp4", "rb") as f:
        await bot.send_video(user_id, f, caption=caption_text)

    os.remove("video.mp4")

else:  # audio
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    with open("audio.mp3", "rb") as f:
        await bot.send_audio(user_id, f, caption=caption_text)

    os.remove("audio.mp3")

    except Exception as e:
        await bot.send_message(user_id, "❌ Download failed.")

    user_links.pop(user_id, None)
    await callback_query.answer()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

