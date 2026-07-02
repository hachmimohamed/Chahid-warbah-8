import os
import psycopg2
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# Initialisation forcée des tables
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (id VARCHAR(50) PRIMARY KEY, points INTEGER DEFAULT 0, miners INTEGER DEFAULT 0);")
        cur.execute("CREATE TABLE IF NOT EXISTS user_tasks (user_id VARCHAR(50), task_name VARCHAR(50), PRIMARY KEY (user_id, task_name));")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erreur init_db: {e}")

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/score', methods=['GET'])
def get_score():
    try:
        uid = request.args.get('telegram_id')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
        res = cur.fetchone()
        score = res[0] if res else 0
        cur.close(); conn.close()
        return jsonify({"score": score})
    except:
        return jsonify({"score": 0})

@app.route('/api/tap', methods=['POST'])
def tap():
    try:
        uid = str(request.json.get('telegram_id'))
        conn = get_db_connection()
        cur = conn.cursor()
        # Insertion sécurisée
        cur.execute("""
            INSERT INTO users (id, points, miners) VALUES (%s, 1, 0) 
            ON CONFLICT (id) DO UPDATE SET points = users.points + 1 + users.miners
        """, (uid,))
        cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
        score = cur.fetchone()[0]
        conn.commit()
        cur.close(); conn.close()
        return jsonify({"new_score": score})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/complete_task', methods=['POST'])
def complete_task():
    try:
        data = request.json
        uid, task, bonus = str(data.get('telegram_id')), data.get('task_name'), int(data.get('bonus', 600))
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (id, points) VALUES (%s, %s) ON CONFLICT (id) DO UPDATE SET points = users.points + %s", (uid, bonus, bonus))
        cur.execute("INSERT INTO user_tasks (user_id, task_name) VALUES (%s, %s) ON CONFLICT DO NOTHING", (uid, task))
        conn.commit()
        cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
        score = cur.fetchone()[0]
        cur.close(); conn.close()
        return jsonify({"success": True, "new_score": score})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
