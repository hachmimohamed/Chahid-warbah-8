import os
import threading
from flask import Flask
from telegram.ext import Updater, CommandHandler

# 1. Configuration du serveur Web minimaliste (pour garder le bot en vie sur Render)
app = Flask(__name__)

@app.route('/')
def home():
    # Ici, on retourne juste du texte simple. 
    # Plus besoin de fichier index.html, donc plus d'erreur !
    return "Le bot Telegram est en ligne et actif."

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# 2. Votre logique Telegram
def start(update, context):
    update.message.reply_text("Bonjour ! Le bot est connecté et prêt à fonctionner.")

def main():
    # Récupération du token depuis les variables d'environnement sur Render
    token = os.getenv("EXE_API_TOKEN")
    
    if not token:
        print("Erreur : La variable EXE_API_TOKEN n'est pas configurée sur Render.")
        return

    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    # Vos commandes
    dp.add_handler(CommandHandler("start", start))

    # Démarrage du bot
    print("Démarrage du bot Telegram...")
    updater.start_polling()
    updater.idle()

# 3. Exécution
if __name__ == "__main__":
    # Lance le serveur web dans un fil d'exécution séparé (thread)
    threading.Thread(target=run_flask).start()
    # Lance le bot
    main()
