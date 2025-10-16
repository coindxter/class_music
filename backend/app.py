from flask import Flask, jsonify, request, send_from_directory
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import current_app
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import yt_dlp
import os
import re

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

#================

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
        "nochecknocheckcertificate": True,
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

import os
from flask import jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed
import yt_dlp

@app.route("/download_student_songs/<int:student_id>", methods=["GET"])
def download_student_songs(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    songs = Song.query.join(Artist).filter(Artist.student_id == student_id).all()
    if not songs:
        return jsonify({"message": "No songs to download for this student."}), 200

    download_dir = "downloads"
    os.makedirs(download_dir, exist_ok=True)

    def download_song(song):
        try:
            safe_title = "".join(c for c in song.title if c.isalnum() or c in " _-").strip()
            filename = f"{safe_title}.%(ext)s"
            output_path = os.path.join(download_dir, filename)

            ydl_opts = {
                "outtmpl": output_path,
                "format": "bestaudio/best",
                "quiet": True,
                "nocheckcertificate": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([song.link])

            print(f"Downloaded: {song.title}")
            return {"title": song.title, "status": "success"}
        except Exception as e:
            print(f"Failed to download {song.title}: {e}")
            return {"title": song.title, "status": "failed", "error": str(e)}

    results = []
    max_workers = min(5, len(songs))  # cap concurrency at 5
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_song = {executor.submit(download_song, song): song for song in songs}
        for future in as_completed(future_to_song):
            result = future.result()
            results.append(result)

    return jsonify({
        "student": student.name,
        "downloaded": [r for r in results if r["status"] == "success"],
        "failed": [r for r in results if r["status"] == "failed"]
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

    for student in class_item.students:
        for artist in student.artists:
            for song in artist.songs:
                if song.file_path:
                    file_path = os.path.join(DOWNLOAD_DIR, song.file_path)
                    if os.path.exists(file_path):
                        os.remove(file_path)

    db.session.delete(class_item)
    db.session.commit()
    return jsonify({"message": "Class and associated files deleted successfully"}), 200

@app.route("/delete/student/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    for artist in student.artists:
        for song in artist.songs:
            if song.file_path:
                file_path = os.path.join(DOWNLOAD_DIR, song.file_path)
                if os.path.exists(file_path):
                    os.remove(file_path)

    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student and associated files deleted successfully"}), 200

@app.route("/delete/artist/<int:artist_id>", methods=["DELETE"])
def delete_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if not artist:
        return jsonify({"error": "Artist not found"}), 404

    for song in artist.songs:
        if song.file_path:
            file_path = os.path.join(DOWNLOAD_DIR, song.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)

    db.session.delete(artist)
    db.session.commit()
    return jsonify({"message": "Artist and associated files deleted successfully"}), 200

@app.route("/delete/song/<int:song_id>", methods=["DELETE"])
def delete_song(song_id):
    song = Song.query.get(song_id)
    if not song:
        print(f"[DELETE SONG] Song with ID {song_id} not found.")
        return jsonify({"error": "Song not found"}), 404

    if song.file_path:
        file_path = os.path.join(DOWNLOAD_DIR, song.file_path)
        print(f"[DELETE SONG] Deleting file: {file_path}")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"[DELETE SONG] File deleted successfully.")
            except Exception as e:
                print(f"[DELETE SONG] Error deleting file: {e}")
        else:
            print(f"[DELETE SONG] File does not exist at path: {file_path}")
    else:
        print(f"[DELETE SONG] No file_path stored for song {song_id}")

    db.session.delete(song)
    db.session.commit()
    print(f"[DELETE SONG] DB entry deleted for song {song_id}")

    return jsonify({"message": "Song and file deleted successfully"}), 200

@app.route("/delete/all", methods=["DELETE"])
def delete_all():
    try:
        for filename in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        Song.query.delete()
        Artist.query.delete()
        Student.query.delete()
        ClassPeriod.query.delete()
        db.session.commit()

        return jsonify({"message": "All data and files deleted successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/delete/all_downloads", methods=["DELETE"])
def delete_all_downloads():
    try:
        if os.path.exists(DOWNLOAD_DIR):
            for filename in os.listdir(DOWNLOAD_DIR):
                file_path = os.path.join(DOWNLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        return jsonify({"message": "All downloads cleared"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/fetch_top_songs_all", methods=["GET"])
def fetch_top_songs_all():
    try:
        artists = Artist.query.all()
        added_count = 0
        results_summary = {}
        incomplete_artists = []

        base_opts = {
            "nocheckcertificate": True,
            "quiet": True,
            "extract_flat": True,
            "skip_download": True,
            "default_search": None,
            "source_address": "0.0.0.0"
        }

        for artist in artists:
            artist_name = artist.name
            print(f"\nSearching top songs for: {artist_name}")

            top_query = f"ytsearch5:{artist_name} official music video"
            try:
                with yt_dlp.YoutubeDL(base_opts) as ydl:
                    info = ydl.extract_info(top_query, download=False)
                    entries = info.get("entries", [])
            except Exception as e:
                print(f"yt-dlp search failed for {artist_name}: {e}")
                continue

            if not entries:
                print(f"No search results found for {artist_name}")
                incomplete_artists.append(artist_name)
                continue

            top_titles = []
            for entry in entries:
                title = entry.get("title")
                if title:
                    top_titles.append(title)

            if not top_titles:
                incomplete_artists.append(artist_name)
                continue

            valid_songs = []

            for song_title in top_titles[:5]:
                lyric_query = f"ytsearch1:{artist_name} {song_title} lyrics"
                try:
                    with yt_dlp.YoutubeDL(base_opts) as ydl:
                        lyric_info = ydl.extract_info(lyric_query, download=False)
                        lyric_entries = lyric_info.get("entries", [])
                except Exception as e:
                    print(f"Lyric search failed for {song_title}: {e}")
                    continue

                if not lyric_entries:
                    print(f"No lyric video found for {song_title}")
                    continue

                lyric_entry = lyric_entries[0]
                lyric_title = lyric_entry.get("title")
                lyric_video_id = lyric_entry.get("id")

                if lyric_title and lyric_video_id:
                    link = f"https://www.youtube.com/watch?v={lyric_video_id}"
                    valid_songs.append({"title": lyric_title, "link": link})
                    print(f"Matched lyric video: {lyric_title}")

            if not valid_songs:
                incomplete_artists.append(artist_name)
                continue

            results_summary[artist_name] = valid_songs

            for vid in valid_songs:
                existing = Song.query.filter_by(title=vid["title"], artist_id=artist.id).first()
                if not existing:
                    db.session.add(Song(title=vid["title"], link=vid["link"], artist_id=artist.id))
                    added_count += 1

        db.session.commit()

        return jsonify({
            "message": f"Added {added_count} lyric videos total.",
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
