import os
import psycopg2
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Assurez-vous que DATABASE_URL est bien configuré sur Render
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

@app.route('/')
def index():
    # Rendu de la page avec un score initial de 0
    return render_template('index.html', initial_score=0)

@app.route('/api/tap', methods=['POST'])
def tap():
    data = request.json
    uid = str(data.get('telegram_id') or data.get('email'))
    
    if not uid:
        return jsonify({"error": "Identifiant manquant"}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Mise à jour ou insertion
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
        print(f"Erreur DB: {e}")
        return jsonify({"error": "Erreur de sauvegarde"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
