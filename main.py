import telebot
from telebot import types
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
bot = telebot.TeleBot(BOT_TOKEN)
# =====================================

user_links = {}  # Temporary store for user links

# ==================== /start command ====================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "📥 Send Instagram or Pinterest link\n"
        "✅ Reels, Posts, Public Stories supported\n"
        "❌ Private accounts not supported"
    )

# ==================== Receive link ====================
@bot.message_handler(func=lambda message: True)
def get_link(message):
    url = message.text

    if "youtube.com" in url or "youtu.be" in url:
        bot.reply_to(message, "❌ YouTube downloads are not supported on cloud servers.")
        return

    user_links[message.from_user.id] = url

    # Ask Video or Audio
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("🎥 Video", callback_data="video"),
        types.InlineKeyboardButton("🎵 Audio", callback_data="audio")
    )

    bot.send_message(message.chat.id, "What do you want to download?", reply_markup=keyboard)

# ==================== Handle Video / Audio choice ====================
@bot.callback_query_handler(func=lambda call: call.data in ["video", "audio"])
def process_choice(call):
    choice = call.data
    user_id = call.from_user.id
    url = user_links.get(user_id)

    if not url:
        bot.send_message(user_id, "❌ Link expired. Send again.")
        return

    # Send "Processing..." message
    processing_msg = bot.send_message(user_id, "⏳ Processing...")

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
                bot.send_video(user_id, f, caption=caption_text)

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
                bot.send_audio(user_id, f, caption=caption_text)

            os.remove("audio.mp3")

    except Exception as e:
        bot.send_message(
            user_id,
            "❌ Download failed. Make sure the link is public and valid.\n"
            "Downloaded by Nero Bot\nhttps://t.me/VideoDownNeroBot"
        )

    # Delete "Processing..." message
    bot.delete_message(user_id, processing_msg.id)

    # Remove the stored link
    user_links.pop(user_id, None)

# ==================== Start bot polling ====================
bot.infinity_polling()
