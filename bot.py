import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from dotenv import load_dotenv

load_dotenv()

# Utilisation des variables d'environnement
bot = telebot.TeleBot(os.getenv("BOT_API_TOKEN"))
WEBAPP_URL = os.getenv("WEBAPP_URL") # URL de ton hébergeur (https://chahid-warbah-8.onrender.com)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    url_avec_id = f"{WEBAPP_URL}?user_id={user_id}"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(
        text="🚀 Lancer Chahid Warbah 7", 
        web_app=WebAppInfo(url=url_avec_id)
    ))
    bot.send_message(message.chat.id, "Bienvenue ! Clique pour jouer 👇", reply_markup=markup)

if __name__ == '__main__':
    bot.polling()
