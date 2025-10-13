from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import yt_dlp
import os

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")
CORS(app)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "classdj.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "downloads")

DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

db = SQLAlchemy(app)

class ClassPeriod(db.Model):
    __tablename__ = "class_periods"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    students = db.relationship("Student", backref="class_period", cascade="all, delete", lazy=True)

class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    class_id = db.Column(db.Integer, db.ForeignKey("class_periods.id"))
    artists = db.relationship("Artist", backref="student", cascade="all, delete", lazy=True)

class Artist(db.Model):
    __tablename__ = "artists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    songs = db.relationship("Song", backref="artist", cascade="all, delete", lazy=True)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    link = db.Column(db.String(500))
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"))
    file_path = db.Column(db.String(500), nullable=True)


@app.route("/")
def serve_react():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/add_class", methods=["POST"])
def add_class():
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"error": "Missing class name"}), 400
    class_period = ClassPeriod(name=name)
    db.session.add(class_period)
    db.session.commit()
    return jsonify({"message": f'Class "{name}" added successfully'}), 201

@app.route("/add_student", methods=["POST"])
def add_student():
    data = request.get_json()
    name = data.get("name")
    class_id = data.get("class_id")
    if not name or not class_id:
        return jsonify({"error": "Missing name or class_id"}), 400
    student = Student(name=name, class_id=class_id)
    db.session.add(student)
    db.session.commit()
    return jsonify({"message": f"Student {name} added to class {class_id}"}), 201

@app.route("/add_artist", methods=["POST"])
def add_artist():
    data = request.get_json()
    name = data.get("name")
    student_id = data.get("student_id")
    if not name or not student_id:
        return jsonify({"error": "Missing name or student_id"}), 400
    artist = Artist(name=name, student_id=student_id)
    db.session.add(artist)
    db.session.commit()
    return jsonify({"message": f"Artist {name} added to student {student_id}"}), 201

@app.route("/classes_full")
def get_classes_full():
    classes = ClassPeriod.query.all()
    result = []
    for c in classes:
        class_data = {"id": c.id, "name": c.name, "students": []}
        for s in c.students:
            student_data = {"id": s.id, "name": s.name, "artists": []}
            for a in s.artists:
                artist_data = {
                    "id": a.id,
                    "name": a.name,
                    "songs": [{
                        "id": song.id,
                        "title": song.title,
                        "link": song.link,
                        "file_path": song.file_path,
                        "url": f"http://localhost:5050/songs/{song.file_path}" if song.file_path else None
                    } for song in a.songs],
                }
                student_data["artists"].append(artist_data)
            class_data["students"].append(student_data)
        result.append(class_data)
    return jsonify(result)

@app.route("/add_song_auto", methods=["POST"])
def add_song_auto():
    data = request.get_json()
    title = data.get("title")
    artist_id = data.get("artist_id")

    if not title or not artist_id:
        return jsonify({"error": "Missing title or artist_id"}), 400

    artist = Artist.query.get(artist_id)
    if not artist:
        return jsonify({"error": "Artist not found"}), 404

    artist_name = artist.name
    search_query = f"{artist_name} {title} official music video"
    print(f"Searching YouTube for: {search_query}")

    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        "default_search": "ytsearch5"
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            entries = info.get("entries", [])
    except Exception as e:
        return jsonify({"error": f"Search failed: {e}"}), 500

    if not entries:
        return jsonify({"error": "No search results found"}), 404

    best = next((e for e in entries if "official" in e["title"].lower()), entries[0])
    link = f"https://www.youtube.com/watch?v={best['id']}"
    song_title = best["title"]

    existing = Song.query.filter_by(title=song_title, artist_id=artist_id).first()
    if existing:
        return jsonify({"message": "Song already exists.", "song_id": existing.id}), 200

    song = Song(title=song_title, link=link, artist_id=artist_id)
    db.session.add(song)
    db.session.commit()

    return jsonify({
        "message": f"Added '{song_title}' for {artist_name}.",
        "link": link,
        "song_id": song.id
    }), 201

@app.route("/download_student_songs/<int:student_id>", methods=["POST", "GET"])
def download_student_songs(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    downloaded = []
    skipped = []
    failed = []

    for artist in student.artists:
        for song in artist.songs:
            artist_name = artist.name or "UnknownArtist"
            safe_title = song.title.replace(" ", "_").replace("/", "_")
            filename = f"{artist_name}_{safe_title}.mp3"
            filepath = os.path.join(DOWNLOAD_DIR, filename)

            if os.path.exists(filepath):
                skipped.append(song.title)
                song.file_path = filename
                continue

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": filepath,
                "postprocessors": [
                    {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
                ],
                "quiet": False,
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([song.link])

                song.file_path = filename
                downloaded.append(song.title)
                print(f"Downloaded: {song.title}")

            except Exception as e:
                print(f"Failed to download {song.title}: {e}")
                failed.append({"title": song.title, "error": str(e)})

    db.session.commit()

    return jsonify({
        "message": f"Downloaded {len(downloaded)} songs, skipped {len(skipped)}, failed {len(failed)}.",
        "downloaded": downloaded,
        "skipped": skipped,
        "failed": failed
    }), 200


@app.route("/songs/<path:filename>")
def serve_song(filename):
    try:
        return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=False)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@app.route("/delete/class/<int:class_id>", methods=["DELETE"])
def delete_class(class_id):
    class_item = ClassPeriod.query.get(class_id)
    if not class_item:
        return jsonify({"error": "Class not found"}), 404
    db.session.delete(class_item)
    db.session.commit()
    return jsonify({"message": "Class deleted successfully"}), 200

@app.route("/delete/student/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted successfully"}), 200

@app.route("/delete/artist/<int:artist_id>", methods=["DELETE"])
def delete_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if not artist:
        return jsonify({"error": "Artist not found"}), 404
    db.session.delete(artist)
    db.session.commit()
    return jsonify({"message": "Artist deleted successfully"}), 200

@app.route("/delete/song/<int:song_id>", methods=["DELETE"])
def delete_song(song_id):
    song = Song.query.get(song_id)
    if not song:
        return jsonify({"error": "Song not found"}), 404
    db.session.delete(song)
    db.session.commit()
    return jsonify({"message": "Song deleted successfully"}), 200


@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, "index.html")

@app.route("/downloads/<path:filename>")
def serve_download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

@app.route("/list_songs")
def list_songs():
    try:
        files = [
            f for f in os.listdir(DOWNLOAD_FOLDER)
            if f.lower().endswith(".mp3")
        ]
        return jsonify({"songs": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5050, debug=True)
