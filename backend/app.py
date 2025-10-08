# main Flask server

import time
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@db/classdj'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)

def init_db_with_retry(max_retries=10, delay=5):
    for i in range(max_retries):
        try:
            with app.app_context():
                db.create_all()
                print("✅ Database initialized successfully!")
                return
        except OperationalError as e:
            print(f"⚠️ Database not ready (attempt {i+1}/{max_retries}): {e}")
            time.sleep(delay)
    print("❌ Could not connect to database after several attempts. Exiting...")
    raise SystemExit(1)

init_db_with_retry()

@app.route('/')
def home():
    return jsonify({"message": "Backend is running!"})

@app.route('/songs')
def get_songs():
    songs = Song.query.all()
    return jsonify([{"id": s.id, "title": s.title} for s in songs])

@app.route('/add/<title>')
def add_song(title):
    new_song = Song(title=title)
    db.session.add(new_song)
    db.session.commit()
    return jsonify({"message": f"Added song '{title}'"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
