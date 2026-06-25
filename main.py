import os
import psycopg2
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

@app.route('/')
def index():
    # Récupération de l'ID depuis les paramètres (ou valeur par défaut)
    uid = request.args.get('user_id', '6046697939')
    score = 0
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
        result = cur.fetchone()
        if result:
            score = result[0]
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erreur chargement score: {e}")
    
    return render_template('index.html', initial_score=score)

@app.route('/api/tap', methods=['POST'])
def tap():
    data = request.json
    uid = data.get('telegram_id')
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET points = points + 1 WHERE id = %s", (uid,))
        conn.commit()
        cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
        result = cur.fetchone()
        new_score = result[0] if result else 0
        cur.close()
        conn.close()
        return jsonify({"new_score": new_score})
    except Exception as e:
        print(f"Erreur DB: {e}")
        return jsonify({"error": "Erreur de sauvegarde"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
