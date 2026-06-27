import os
import psycopg2
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Assurez-vous que DATABASE_URL est bien configurée dans les variables d'environnement sur Render
# avec la valeur : postgresql://chahid_warbah_8_user:obOmVyrlkSNLR9TWr9Om7OpTPuG3SlKy@dpg-d8vr949o3t8c73bkfmgg-a/chahid_warbah_8
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    # Connexion à la base de données avec sslmode=require (requis pour Render)
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# Fonction pour initialiser la table automatiquement au démarrage
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
        print("Initialisation DB : Table 'users' prête.")
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la DB : {e}")

# Appel de l'initialisation au démarrage de l'application
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
        
        # Mise à jour ou insertion de l'utilisateur
        cur.execute("UPDATE users SET points = points + 1 WHERE id = %s", (uid,))
        if cur.rowcount == 0:
            cur.execute("INSERT INTO users (id, points) VALUES (%s, 1)", (uid, 1))
        
        conn.commit()
        
        # Récupération du score mis à jour
        cur.execute("SELECT points FROM users WHERE id = %s", (uid,))
        new_score = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        return jsonify({"new_score": new_score})
    except Exception as e:
        # En cas d'erreur, on logue l'erreur complète dans les logs Render
        print(f"Erreur API TAP : {str(e)}")
        return jsonify({"error": "Erreur serveur interne"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
