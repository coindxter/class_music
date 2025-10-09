from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from youtubesearchpython import VideosSearch
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
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    link = db.Column(db.String(255))  # ← new field
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
                    "songs": [{"id": song.id, "title": song.title} for song in a.songs],
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
    if not title or not artist_id:
        return jsonify({"error": "Missing title or artist_id"}), 400
    song = Song(title=title, artist_id=artist_id)
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

DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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
    """
    Fetch top 5 YouTube videos per artist categorized as 'Music' and
    that look like individual tracks (not albums, mixes, or compilations).
    """
    try:
        artists = Artist.query.all()
        added_count = 0
        skipped_count = 0
        results_summary = {}
        incomplete_artists = []

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": False,
            "noplaylist": True,
            "extractor_args": {"youtube": {"player_client": ["web"]}},
        }

        for artist in artists:
            artist_name = artist.name
            print(f"\n🎧 Searching top music videos for: {artist_name}")
            valid_songs = []

            for attempt in range(3):
                print(f"  Attempt {attempt + 1}...")
                search = VideosSearch(f"{artist_name} songs", limit=10)
                results = search.result().get("result", [])
                time.sleep(random.uniform(0.6, 1.3))  # avoid throttling

                for vid in results:
                    link = vid["link"]

                    try:
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(link, download=False)

                        category = info.get("categories", [])
                        title = info.get("title") or ""
                        uploader = info.get("uploader") or ""
                        lower_title = title.lower()

                        # ✅ Only consider Music category
                        if category and "Music" in category:

                            # ❌ Skip compilations, playlists, albums, etc.
                            if any(bad in lower_title for bad in [
                                "mix", "full album", "best of", "compilation",
                                "playlist", "hour", "non stop", "non-stop",
                                "greatest hits", "collection", "discography"
                            ]):
                                print(f"⏭️ Skipped compilation: {title}")
                                continue

                            # ✅ Keep likely single-track titles
                            if "-" in title or len(title.split()) <= 10:
                                if title not in [s["title"] for s in valid_songs]:
                                    valid_songs.append({
                                        "title": title,
                                        "link": link,
                                        "uploader": uploader
                                    })
                                    print(f"🎵 Added {title}")

                    except Exception as e:
                        print(f"⚠️ Skipping {link}: {e}")
                        continue

                if len(valid_songs) >= 5:
                    break  # stop early once we have enough

            if not valid_songs:
                print(f"⚠️ No valid music videos found for {artist_name}")
                incomplete_artists.append(artist_name)
                continue

            top_songs = valid_songs[:5]
            results_summary[artist_name] = []

            for vid in top_songs:
                title = vid["title"]
                link = vid["link"]

                existing = Song.query.filter_by(title=title, artist_id=artist.id).first()
                if existing:
                    skipped_count += 1
                    continue

                new_song = Song(title=title, link=link, artist_id=artist.id)
                db.session.add(new_song)
                added_count += 1
                results_summary[artist_name].append({
                    "title": title,
                    "link": link,
                    "uploader": vid["uploader"]
                })

            if len(top_songs) < 5:
                incomplete_artists.append(artist_name)
                print(f"⚠️ Only found {len(top_songs)} songs for {artist_name}")

        db.session.commit()
        print(f"\n✅ Added {added_count} songs (skipped {skipped_count})")

        return jsonify({
            "message": f"Added {added_count} songs (skipped {skipped_count}).",
            "incomplete_artists": incomplete_artists,
            "data": results_summary
        }), 200

    except Exception as e:
        db.session.rollback()
        print("❌ Error fetching songs:", e)
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="localhost", port=5050, debug=True)
