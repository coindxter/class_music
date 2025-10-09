from flask import Flask, jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@db/classdj'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class ClassPeriod(db.Model):
    __tablename__ = 'class_periods'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    students = db.relationship('Student', backref='class_period', lazy=True)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    class_id = db.Column(db.Integer, db.ForeignKey('class_periods.id'))
    artists = db.relationship('Artist', backref='student', lazy=True)

class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    songs = db.relationship('Song', backref='artist', lazy=True)

class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))

@app.route('/')
def home():
    return jsonify({'message': 'Backend is running!'})

@app.route('/classes')
def get_classes():
    classes = ClassPeriod.query.all()
    return jsonify([{'id': c.id, 'name': c.name} for c in classes])

@app.route('/classes_full')
def get_classes_full():
    """Return full nested data: ClassPeriod -> Students -> Artists -> Songs"""
    classes = ClassPeriod.query.all()

    result = []
    for c in classes:
        class_data = {
            'id': c.id,
            'name': c.name,
            'students': []
        }

        for s in c.students:
            student_data = {
                'id': s.id,
                'name': s.name,
                'artists': []
            }

            for a in s.artists:
                artist_data = {
                    'id': a.id,
                    'name': a.name,
                    'songs': [{'id': song.id, 'title': song.title} for song in a.songs]
                }
                student_data['artists'].append(artist_data)

            class_data['students'].append(student_data)

        result.append(class_data)

    return jsonify(result)

@app.route('/add_class', methods=['POST'])
def add_class():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Missing class name'}), 400

    class_period = ClassPeriod(name=name)
    db.session.add(class_period)
    db.session.commit()
    return jsonify({'message': f'Class "{name}" added successfully'}), 201

@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.get_json()
    name = data.get('name')
    class_id = data.get('class_id')
    if not name or not class_id:
        return jsonify({'error': 'Missing name or class_id'}), 400

    student = Student(name=name, class_id=class_id)
    db.session.add(student)
    db.session.commit()
    return jsonify({'message': f'Student {name} added to class {class_id}'}), 201

@app.route('/add_artist', methods=['POST'])
def add_artist():
    data = request.get_json()
    name = data.get('name')
    student_id = data.get('student_id')
    if not name or not student_id:
        return jsonify({'error': 'Missing name or student_id'}), 400

    artist = Artist(name=name, student_id=student_id)
    db.session.add(artist)
    db.session.commit()
    return jsonify({'message': f'Artist {name} added to student {student_id}'}), 201

@app.route('/add_song', methods=['POST'])
def add_song():
    data = request.get_json()
    title = data.get('title')
    artist_id = data.get('artist_id')
    if not title or not artist_id:
        return jsonify({'error': 'Missing title or artist_id'}), 400

    song = Song(title=title, artist_id=artist_id)
    db.session.add(song)
    db.session.commit()
    return jsonify({'message': f'Song {title} added to artist {artist_id}'}), 201

@app.route('/delete/class/<int:class_id>', methods=['DELETE'])
def delete_class(class_id):
    class_item = ClassPeriod.query.get(class_id)
    if not class_item:
        return jsonify({'error': 'Class not found'}), 404
    db.session.delete(class_item)
    db.session.commit()
    return jsonify({'message': 'Class deleted successfully'}), 200

@app.route('/delete/student/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    db.session.delete(student)
    db.session.commit()
    return jsonify({'message': 'Student deleted successfully'}), 200

@app.route('/delete/artist/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if not artist:
        return jsonify({'error': 'Artist not found'}), 404
    db.session.delete(artist)
    db.session.commit()
    return jsonify({'message': 'Artist deleted successfully'}), 200

@app.route('/delete/song/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    song = Song.query.get(song_id)
    if not song:
        return jsonify({'error': 'Song not found'}), 404
    db.session.delete(song)
    db.session.commit()
    return jsonify({'message': 'Song deleted successfully'}), 200

@app.route('/delete/all', methods=['DELETE'])
def delete_all():
    """Delete ALL data — classes, students, artists, and songs"""
    try:
        num_songs = Song.query.delete()
        num_artists = Artist.query.delete()
        num_students = Student.query.delete()
        num_classes = ClassPeriod.query.delete()
        db.session.commit()
        return jsonify({
            'message': 'All data deleted successfully!',
            'deleted': {
                'classes': num_classes,
                'students': num_students,
                'artists': num_artists,
                'songs': num_songs
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5050, debug=True)
