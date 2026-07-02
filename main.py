import os
import psycopg2
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/shorten', methods=['POST'])
def shorten_link():
    return jsonify({"short_url": request.json.get('url')})

@app.route('/api/complete_task', methods=['POST'])
def complete_task():
    data = request.json
    uid, task, bonus = str(data.get('telegram_id')), data.get('task_name'), int(data.get('bonus', 600))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET points = points + %s WHERE id = %s", (bonus, uid))
    cur.execute("INSERT INTO user_tasks (user_id, task_name) VALUES (%s, %s) ON CONFLICT DO NOTHING", (uid, task))
    conn.commit()
    cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
    score = cur.fetchone()[0]
    cur.close(); conn.close()
    return jsonify({"success": True, "new_score": score})

@app.route('/api/buy_miner', methods=['POST'])
def buy_miner():
    uid = str(request.json.get('telegram_id'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
    res = cur.fetchone()
    if res and res[0] >= 10000:
        cur.execute("UPDATE users SET points = points - 10000, miners = miners + 1 WHERE id = %s", (uid,))
        conn.commit()
        cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
        new_score = cur.fetchone()[0]
        cur.close(); conn.close()
        return jsonify({"success": True, "new_score": new_score})
    cur.close(); conn.close()
    return jsonify({"success": False, "message": "Solde insuffisant"})

@app.route('/api/tap', methods=['POST'])
def tap():
    uid = str(request.json.get('telegram_id'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT miners FROM users WHERE id = %s", (uid,))
    res = cur.fetchone()
    miners = res[0] if res else 0
    cur.execute("UPDATE users SET points = points + %s WHERE id = %s", (1 + miners, uid))
    cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
    score = cur.fetchone()[0]
    conn.commit()
    cur.close(); conn.close()
    return jsonify({"new_score": score})

@app.route('/api/score', methods=['GET'])
def get_score():
    uid = request.args.get('telegram_id')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
    res = cur.fetchone()
    return jsonify({"score": res[0] if res else 0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
