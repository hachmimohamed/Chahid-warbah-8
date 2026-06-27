import os
import psycopg2
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

@app.route('/')
def index():
    return render_template('index.html', initial_score=0)

@app.route('/api/score', methods=['GET'])
def get_score():
    uid = request.args.get('telegram_id')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
        result = cur.fetchone()
        score = result[0] if result else 0
        cur.close()
        conn.close()
        return jsonify({"score": score})
    except:
        return jsonify({"score": 0})

@app.route('/api/tap', methods=['POST'])
def tap():
    data = request.json
    uid = str(data.get('telegram_id'))
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET points = points + 1 WHERE id = %s", (uid,))
        if cur.rowcount == 0:
            cur.execute("INSERT INTO users (id, points) VALUES (%s, 1)", (uid, 1))
        conn.commit()
        cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
        new_score = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify({"new_score": new_score})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
