import os
import psycopg2
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Assurez-vous que DATABASE_URL est bien dans l'onglet Environment de Render
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

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
        print("Initialisation : Table 'users' prête.")
    except Exception as e:
        print(f"Erreur init_db : {e}")

init_db()

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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tap', methods=['POST'])
def tap():
    data = request.json
    uid = str(data.get('telegram_id'))
    # Récupération du bonus envoyé (600 pour la mission, sinon 1 par défaut)
    bonus = int(data.get('bonus', 1)) 
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Mise à jour avec le bonus dynamique
        cur.execute("UPDATE users SET points = points + %s WHERE id = %s", (bonus, uid))
        if cur.rowcount == 0:
            cur.execute("INSERT INTO users (id, points) VALUES (%s, %s)", (uid, bonus))
        
        conn.commit()
        
        cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
        new_score = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        return jsonify({"new_score": new_score})
    except Exception as e:
        print(f"Erreur API TAP : {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
