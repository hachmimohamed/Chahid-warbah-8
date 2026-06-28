import os
import psycopg2
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# Route pour la gestion des missions
@app.route('/api/shorten', methods=['POST'])
def shorten_link():
    data = request.json
    service = data.get('service')
    url = data.get('url')
    # Récupère les clés depuis les variables d'environnement Render (EXE_API_KEY et LINKJUST_API_KEY)
    api_key = os.environ.get("EXE_API_KEY") if service == 'exe' else os.environ.get("LINKJUST_API_KEY")
    base_url = "https://exe.io/api" if service == 'exe' else "https://linkjust.com/api"
    
    try:
        res = requests.get(f"{base_url}?api={api_key}&url={url}&format=text")
        return jsonify({"short_url": res.text})
    except:
        return jsonify({"short_url": ""})

@app.route('/api/tap', methods=['POST'])
def tap():
    data = request.json
    uid = str(data.get('telegram_id'))
    bonus = int(data.get('bonus', 1))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET points = points + %s WHERE id = %s", (bonus, uid))
    if cur.rowcount == 0:
        cur.execute("INSERT INTO users (id, points) VALUES (%s, %s)", (uid, bonus))
    conn.commit()
    cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
    new_score = cur.fetchone()[0]
    cur.close()
    conn.close()
    return jsonify({"new_score": new_score})

@app.route('/api/score', methods=['GET'])
def get_score():
    uid = request.args.get('telegram_id')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
    result = cur.fetchone()
    score = result[0] if result else 0
    cur.close()
    conn.close()
    return jsonify({"score": score})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
