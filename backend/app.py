# main Flask server

from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, ClassPeriod, Student, Artist, Song
import time

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@db/classdj'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    retries = 10
    for i in range(retries):
        try:
            db.create_all()
            print("Database connected and tables created!")
            break
        except Exception as e:
            print(f"Database not ready (attempt {i+1}/{retries}): {e}")
            time.sleep(3)
    else:
        print("Could not connect to database after several attempts.")


@app.route('/')
def index():
    return jsonify({"message": "Backend is running!"})

@app.route('/add_class', methods=['POST'])
def add_class():
    data = request.get_json()
    name = data.get('name')
    new_class = ClassPeriod(name=name)
    db.session.add(new_class)
    db.session.commit()
    return jsonify({"message": f"Class '{name}' added"})

@app.route('/classes', methods=['GET'])
def get_classes():
    classes = ClassPeriod.query.all()
    return jsonify([{"id": c.id, "name": c.name} for c in classes])

@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.get_json()
    name = data.get('name')
    class_id = data.get('class_id')
    new_student = Student(name=name, class_id=class_id)
    db.session.add(new_student)
    db.session.commit()
    return jsonify({"message": f"Student '{name}' added to class {class_id}"})

@app.route('/students/<int:class_id>', methods=['GET'])
def get_students(class_id):
    students = Student.query.filter_by(class_id=class_id).all()
    return jsonify([{"id": s.id, "name": s.name} for s in students])

@app.route('/add_artist', methods=['POST'])
def add_artist():
    data = request.get_json()
    name = data.get('name')
    student_id = data.get('student_id')
    new_artist = Artist(name=name, student_id=student_id)
    db.session.add(new_artist)
    db.session.commit()
    return jsonify({"message": f"Artist '{name}' added to student {student_id}"})

@app.route('/artists/<int:student_id>', methods=['GET'])
def get_artists(student_id):
    artists = Artist.query.filter_by(student_id=student_id).all()
    return jsonify([{"id": a.id, "name": a.name} for a in artists])

@app.route('/add_song', methods=['POST'])
def add_song():
    data = request.get_json()
    title = data.get('title')
    artist_id = data.get('artist_id')
    new_song = Song(title=title, artist_id=artist_id)
    db.session.add(new_song)
    db.session.commit()
    return jsonify({"message": f"Song '{title}' added to artist {artist_id}"})

@app.route('/songs/<int:artist_id>', methods=['GET'])
def get_songs(artist_id):
    songs = Song.query.filter_by(artist_id=artist_id).all()
    return jsonify([{"id": s.id, "title": s.title} for s in songs])

@app.route('/full', methods=['GET'])
def get_full_structure():
    data = []
    classes = ClassPeriod.query.all()
    for c in classes:
        class_data = {"class": c.name, "students": []}
        for s in c.students:
            student_data = {"name": s.name, "artists": []}
            for a in s.artists:
                artist_data = {
                    "name": a.name,
                    "songs": [song.title for song in a.songs]
                }
                student_data["artists"].append(artist_data)
            class_data["students"].append(student_data)
        data.append(class_data)
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)