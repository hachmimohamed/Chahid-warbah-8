import os
import psycopg2
import requests
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_tasks (
                user_id VARCHAR(50),
                task_name VARCHAR(50),
                last_done TIMESTAMP,
                PRIMARY KEY (user_id, task_name)
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erreur init_db: {e}")

@app.route('/api/shorten', methods=['POST'])
def shorten_link():
    data = request.json
    service = data.get('service')
    url = data.get('url')
    api_key = os.environ.get("EXE_API_KEY") if service == 'exe' else os.environ.get("LINKJUST_API_KEY")
    
    if not api_key:
        return jsonify({"error": "Clé API manquante"}), 500
        
    try:
        if service == 'linkjust':
            api_call = f"https://linkjust.com/api?api={api_key}&url={url}"
            res = requests.get(api_call, timeout=10)
            if res.status_code == 200:
                result = res.json()
                if result.get("status") == "success":
                    return jsonify({"short_url": result.get("shortenedUrl")})
                return jsonify({"error": f"Linkjust: {result.get('message', 'Erreur')}"}), 400
            return jsonify({"error": "Erreur connexion Linkjust"}), 500
        else:
            api_call = f"https://exe.io/api?api={api_key}&url={url}&format=text"
            res = requests.get(api_call, timeout=10)
            if res.status_code == 200:
                return jsonify({"short_url": res.text})
            return jsonify({"error": "Service indisponible"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/complete_task', methods=['POST'])
def complete_task():
    data = request.json
    uid = str(data.get('telegram_id'))
    task_name = data.get('task_name') 
    bonus = int(data.get('bonus', 600))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT last_done FROM user_tasks WHERE user_id = %s AND task_name = %s", (uid, task_name))
    res = cur.fetchone()
    
    if res and res[0] > datetime.now() - timedelta(hours=24):
        cur.close()
        conn.close()
        return jsonify({"success": False, "message": "Déjà fait aujourd'hui"})
    
    cur.execute("UPDATE users SET points = points + %s WHERE id = %s", (bonus, uid))
    cur.execute("""
        INSERT INTO user_tasks (user_id, task_name, last_done) 
        VALUES (%s, %s, %s) 
        ON CONFLICT (user_id, task_name) DO UPDATE SET last_done = %s
    """, (uid, task_name, datetime.now(), datetime.now()))
    conn.commit()
    cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
    new_score = cur.fetchone()[0]
    cur.close()
    conn.close()
    return jsonify({"success": True, "new_score": new_score})

@app.route('/api/buy_miner', methods=['POST'])
def buy_miner():
    data = request.json
    uid = str(data.get('telegram_id'))
    cost = 10000
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
    res = cur.fetchone()
    if res and res[0] >= cost:
        cur.execute("UPDATE users SET points = points - %s WHERE id = %s", (cost, uid))
        conn.commit()
        cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
        new_score = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify({"success": True, "new_score": new_score})
    cur.close()
    conn.close()
    return jsonify({"success": False, "message": "Solde insuffisant"})

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
    res = cur.fetchone()
    score = res[0] if res else 0
    cur.close()
    conn.close()
    return jsonify({"score": score})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
