import os
import psycopg2
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    # Suppression de sslmode='require' si cela bloque la connexion
    # Si cela échoue, essayez de remettre 'sslmode=require'
    return psycopg2.connect(DATABASE_URL)

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(255) PRIMARY KEY,
                points INTEGER DEFAULT 0
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Table 'users' prête.")
    except Exception as e:
        print(f"Erreur init_db: {e}")

init_db()

@app.route('/')
def index():
    return render_template('index.html', initial_score=0)

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
