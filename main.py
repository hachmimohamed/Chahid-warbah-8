import os
import urllib.parse
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import requests

load_dotenv() 

app = Flask(__name__)

# Configuration de la base de données
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Récupération sécurisée des jetons via variables d'environnement
EXE_API_TOKEN = os.getenv("EXE_API_TOKEN")
LINKJUST_API_TOKEN = os.getenv("LINKJUST_API_TOKEN")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(50), unique=True)
    balance = db.Column(db.Integer, default=0)
    multitap_level = db.Column(db.Integer, default=1)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    user_id = request.args.get('user_id')
    user = User.query.filter_by(telegram_id=str(user_id)).first()
    if not user:
        user = User(telegram_id=str(user_id))
        db.session.add(user)
        db.session.commit()
    return render_template('index.html', initial_score=user.balance)

@app.route('/api/tap', methods=['POST'])
def tap():
    data = request.json or {}
    uid = str(data.get('telegram_id'))
    user = User.query.filter_by(telegram_id=uid).first()
    if user:
        user.balance += (1 * user.multitap_level)
        db.session.commit()
    return jsonify({"success": True, "new_score": user.balance if user else 0})

@app.route('/api/get_short_link', methods=['POST'])
def get_short_link():
    data = request.json or {}
    mission_type = data.get('mission_type')
    tg_id = str(data.get('user_id'))
    url_cible = "https://t.me/ChahidWarbah7"
    
    if mission_type == 'exe':
        res = requests.get(f"https://exe.io/api?api={EXE_API_TOKEN}&url={urllib.parse.quote(url_cible)}&subid={tg_id}")
        return jsonify({"success": True, "short_url": res.json().get('shortenedUrl', url_cible)})
    return jsonify({"success": False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
