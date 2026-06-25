import os
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Le bot Telegram est en ligne."

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    # Mettez ici votre code de démarrage du bot Telegram (ex: updater.start_polling())
