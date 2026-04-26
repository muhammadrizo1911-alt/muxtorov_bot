import telebot
import time
import threading
import os
from datetime import datetime, timedelta

TOKEN = '8574031918:AAEhTsSOo-wcjbJc3if7iWMg7mbWlPKnyAs'
ADMIN_ID = int(os.environ.get('ADMIN_ID', '6917006135'))

bot = telebot.TeleBot(TOKEN)

pending_messages = {}

AUTO_REPLY_TEXT = """Assalomu alaykum! 👋

Hozircha admin online emas. 
Xabaringiz qabul qilindi. 
Tez orada (1 soat ichida) javob beramiz.

Rahmat!"""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
        f"Assalomu alaykum {message.from_user.first_name}! 👋\n"
        "Savol yoki xabaringiz bo'lsa yozing. Tez orada javob beriladi."
    )

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message,
        "📌 Yordam:\n"
        "• Xabar yozing — admin ko'radi\n"
        "• Javob kelguncha kuting\n"
        "• Savolingiz bo'lsa bemalol yozing!"
    )

@bot.message_handler(func=lambda m: m.chat.id != ADMIN_ID)
def handle_user_message(message):
    user_id = message.chat.id
    username = message.from_user.username or "yo'q"
    first_name = message.from_user.first_name or ""

    try:
        bot.forward_message(ADMIN_ID, user_id, message.message_id)
        bot.send_message(
            ADMIN_ID,
            f"👤 Ism: {first_name}\n🔗 Username: @{username}\n🆔 ID: {user_id}"
        )
    except Exception as e:
        print(f"Forward xatolik: {e}")

    bot.reply_to(message, "✅ Xabaringiz qabul qilindi. Tez orada javob beramiz!")
    pending_messages[user_id] = {"time": datetime.now()}
    threading.Thread(target=check_for_auto_reply, args=(user_id,), daemon=True).start()

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID)
def handle_admin_reply(message):
    try:
        if message.reply_to_message and message.reply_to_message.forward_from:
            user_id = message.reply_to_message.forward_from.id
            bot.send_message(user_id, f"💬 Admin javobi:\n\n{message.text}")
            bot.reply_to(message, "✅ Javob yuborildi!")
            if user_id in pending_messages:
                del pending_messages[user_id]
        else:
            bot.reply_to(message, "❌ Javob yuborish uchun foydalanuvchi xabariga reply qiling.")
    except Exception as e:
        print(f"Admin javob xatolik: {e}")

def check_for_auto_reply(user_id):
    time.sleep(600)
    if user_id in pending_messages:
        if datetime.now() - pending_messages[user_id]["time"] > timedelta(minutes=10):
            try:
                bot.send_message(user_id, AUTO_REPLY_TEXT)
            except Exception as e:
                print(f"Avto-javob xatolik: {e}")
            if user_id in pending_messages:
                del pending_messages[user_id]

print(f"Bot ishga tushdi ✅ | Admin ID: {ADMIN_ID}")
bot.infinity_polling(timeout=60, long_polling_timeout=60)
