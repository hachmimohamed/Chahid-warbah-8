import os
import psycopg2
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Récupération de l'URL de la base depuis les variables d'environnement Render
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    # Connexion à PostgreSQL
    return psycopg2.connect(DATABASE_URL, sslmode='require')

@app.route('/')
def index():
    # Exemple pour charger les points au démarrage
    # Tu devras créer la table 'users' dans ta base distante si ce n'est pas fait
    return render_template('index.html')

@app.route('/api/tap', methods=['POST'])
def tap():
    data = request.json
    uid = data.get('telegram_id')
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Mise à jour sécurisée avec %s (syntaxe Postgres)
        cur.execute("UPDATE users SET points = points + 1 WHERE id = %s", (uid,))
        conn.commit()
        
        # Récupération du score mis à jour
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
