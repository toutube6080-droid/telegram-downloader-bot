from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import yt_dlp
import os
import threading
from flask import Flask

# ================== Flask keep-alive for Render ==================
app = Flask(__name__)

@app.route("/")
def home():
    return "Nero Bot is alive!"

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()
# ==================================================================

# ===== Enter your bot token here =====
BOT_TOKEN = "8304098491:AAFzuQnfAS3dy3bnjIh0IG8vP3bsNHChj5A"
# =====================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

user_links = {}  # Temporary store for user links

# ==================== /start command ====================
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply(
        "📥 Send Instagram or Pinterest link\n"
        "✅ Reels, Posts, Public Stories supported\n"
        "❌ Private accounts not supported"
    )

# ==================== Receive link ====================
@dp.message_handler()
async def get_link(message: types.Message):
    url = message.text

    # Block YouTube links on Render
    if "youtube.com" in url or "youtu.be" in url:
        await message.reply("❌ YouTube downloads are not supported on cloud servers.")
        return

    user_links[message.from_user.id] = url

    # Ask Video or Audio
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🎥 Video", callback_data="video"),
        InlineKeyboardButton("🎵 Audio", callback_data="audio")
    )

    await message.reply("What do you want to download?", reply_markup=keyboard)

# ==================== Handle Video / Audio choice ====================
@dp.callback_query_handler(lambda c: c.data in ["video", "audio"])
async def process_choice(callback_query: types.CallbackQuery):
    choice = callback_query.data
    user_id = callback_query.from_user.id
    url = user_links.get(user_id)

    if not url:
        await callback_query.message.reply("❌ Link expired. Send again.")
        return

    # Send "Processing..." message and store it
    processing_msg = await callback_query.message.edit_text("⏳ Processing...")

    # Caption with your bot name and username
    caption_text = "Downloaded by Nero Bot\nhttps://t.me/VideoDownNeroBot"

    try:
        if choice == "video":
            ydl_opts = {
                'format': 'mp4',
                'outtmpl': 'video.%(ext)s'
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            with open("video.mp4", "rb") as f:
                await bot.send_video(user_id, f, caption=caption_text)

            os.remove("video.mp4")

        else:  # audio
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'audio.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            with open("audio.mp3", "rb") as f:
                await bot.send_audio(user_id, f, caption=caption_text)

            os.remove("audio.mp3")

        # ✅ Delete the "Processing..." message after success
        await processing_msg.delete()

    except Exception as e:
        # Delete "Processing..." before sending error
        await processing_msg.delete()
        await bot.send_message(
            user_id,
            "❌ Download failed. Make sure the link is public and valid.\n"
            "Downloaded by Nero Bot\nhttps://t.me/VideoDownNeroBot"
        )

    # Remove the stored link
    user_links.pop(user_id, None)
    await callback_query.answer()

# ==================== Start bot polling ====================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
