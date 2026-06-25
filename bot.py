import os
import threading
from flask import Flask
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# 1. Configuration du serveur Web (Obligatoire pour Render)
app = Flask(__name__)

@app.route('/')
def home():
    return "Le bot est en ligne !"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# 2. Votre logique Telegram
def start(update, context):
    update.message.reply_text("Bonjour ! Le bot est actif.")

def main():
    # Récupération du token depuis les variables d'environnement Render
    token = os.getenv("EXE_API_TOKEN")
    
    if not token:
        print("Erreur : Le token EXE_API_TOKEN n'est pas défini.")
        return

    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    # Vos commandes
    dp.add_handler(CommandHandler("start", start))

    # Démarrage du bot
    print("Bot démarré...")
    updater.start_polling()
    updater.idle()

# 3. Exécution simultanée
if __name__ == "__main__":
    # Lance le serveur Web dans un thread séparé
    threading.Thread(target=run_flask).start()
    # Lance le bot
    main()
