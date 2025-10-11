from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import yt_dlp
import os
import uuid
import requests
import time
import random

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")
CORS(app)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "classdj.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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


@app.route("/")
def serve_react():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/classes")
def get_classes():
    classes = ClassPeriod.query.all()
    return jsonify([{"id": c.id, "name": c.name} for c in classes])

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
                    "songs": [{"id": song.id, "title": song.title, "link": song.link} for song in a.songs],
                }
                student_data["artists"].append(artist_data)
            class_data["students"].append(student_data)
        result.append(class_data)
    return jsonify(result)


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

@app.route("/add_song", methods=["POST"])
def add_song():
    data = request.get_json()
    title = data.get("title")
    artist_id = data.get("artist_id")
    link = data.get("link", "")
    if not title or not artist_id:
        return jsonify({"error": "Missing title or artist_id"}), 400
    song = Song(title=title, link=link, artist_id=artist_id)
    db.session.add(song)
    db.session.commit()
    return jsonify({"message": f"Song {title} added to artist {artist_id}"}), 201

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

@app.route("/delete/all", methods=["DELETE"])
def delete_all():
    try:
        Song.query.delete()
        Artist.query.delete()
        Student.query.delete()
        ClassPeriod.query.delete()
        db.session.commit()
        return jsonify({"message": "All data deleted successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def download_mp3_from_youtube(url, artist_name):
    safe_artist = artist_name.replace(" ", "_")
    filename = f"{safe_artist}_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": filepath,
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
        ],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return filepath

@app.route("/fetch_top_songs_all", methods=["GET"])
def fetch_top_songs_all():
    try:
        artists = Artist.query.all()
        added_count = 0
        results_summary = {}
        incomplete_artists = []

        for artist in artists:
            artist_name = artist.name
            print(f"\nSearching top songs for: {artist_name}")

            ydl_opts = {
                "quiet": True,
                "extract_flat": True,
                "skip_download": True,
                "default_search": None,   
                "source_address": "0.0.0.0"  
            }

            query = f"ytsearch5:{artist_name} official music video"

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(query, download=False)
                    entries = info.get("entries", [])
            except Exception as e:
                print(f"yt-dlp search failed for {artist_name}: {e}")
                continue

            if not entries:
                print(f"No search results found for {artist_name}")
                incomplete_artists.append(artist_name)
                continue

            valid_songs = []
            for entry in entries:
                title = entry.get("title")
                video_id = entry.get("id")
                if not title or not video_id:
                    continue
                link = f"https://www.youtube.com/watch?v={video_id}"
                valid_songs.append({"title": title, "link": link})
                print(f"🎵 Found: {title}")

            if not valid_songs:
                incomplete_artists.append(artist_name)
                continue

            results_summary[artist_name] = valid_songs

            # save to DB
            for vid in valid_songs[:5]:
                existing = Song.query.filter_by(title=vid["title"], artist_id=artist.id).first()
                if not existing:
                    db.session.add(Song(title=vid["title"], link=vid["link"], artist_id=artist.id))
                    added_count += 1

        db.session.commit()
        print(f"\nAdded {added_count} songs total")

        return jsonify({
            "message": f"Added {added_count} songs total.",
            "incomplete_artists": incomplete_artists,
            "data": results_summary
        }), 200

    except Exception as e:
        db.session.rollback()
        print("Error fetching songs:", e)
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5050, debug=True)
