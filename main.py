import os
import psycopg2
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

@app.route('/api/shorten', methods=['POST'])
def shorten_link():
    data = request.json
    service = data.get('service') # Sera 'exe' ou 'linkjust'
    url = data.get('url')
    
    api_key = os.environ.get("EXE_API_KEY") if service == 'exe' else os.environ.get("LINKJUST_API_KEY")
    
    if not api_key:
        return jsonify({"error": "Clé API manquante"}), 500
        
    try:
        # LOGIQUE SÉPARÉE POUR CHAQUE SERVICE
        if service == 'linkjust':
            # Appel spécifique pour Linkjust (JSON)
            api_call = f"https://linkjust.com/api?api={api_key}&url={url}"
            res = requests.get(api_call, timeout=10)
            if res.status_code == 200:
                return jsonify({"short_url": res.json().get('shortenedUrl')})
        
        else: 
            # Appel spécifique pour Exe.io (Texte)
            api_call = f"https://exe.io/api?api={api_key}&url={url}&format=text"
            res = requests.get(api_call, timeout=10)
            if res.status_code == 200:
                return jsonify({"short_url": res.text})
            
        return jsonify({"error": "API refusée"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ... (Gardez le reste de votre code inchangé : /api/tap, /api/score, etc.)
