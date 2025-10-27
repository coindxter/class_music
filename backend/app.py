from flask import Flask, jsonify, request, send_from_directory
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import yt_dlp
import os
import re
import threading
import requests
from sqlalchemy.orm import scoped_session, sessionmaker


# -------------------- App / SocketIO / DB --------------------

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")
socketio = SocketIO(app, cors_allowed_origins="*")  
CORS(app)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PERSIST_DIR = os.path.join(BASE_DIR, "persistent")
os.makedirs(PERSIST_DIR, exist_ok=True)

db_path = os.path.join(PERSIST_DIR, "classdj.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

db = SQLAlchemy(app)

# -------------------- Models --------------------

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

# -------------------- Helpers --------------------

#this works

def get_soundcloud_client_id():

    resp = requests.get("https://soundcloud.com/", timeout=10)
    resp.raise_for_status()
    js_urls = re.findall(r'src="(https://a-v2\.sndcdn\.com/assets/[^"]+\.js)"', resp.text)
    if not js_urls:
        raise RuntimeError("No SoundCloud asset JS URLs found on homepage")

    for url in js_urls:
        js = requests.get(url, timeout=10).text
        m = re.search(r'client_id\s*:\s*"([a-zA-Z0-9]{32})"', js)
        if m:
            return m.group(1)
        m2 = re.search(r'client_id"\s*:\s*"([a-zA-Z0-9]{32})"', js)
        if m2:
            return m2.group(1)

    raise RuntimeError("Could not extract SoundCloud client_id from JS")




# -------------------- Routes --------------------

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

# -----------------------------------------------

#change to download from soundcloud
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
        "nocheckcertificate": True,  
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

    best = next((e for e in entries if "official" in e.get("title", "").lower()), entries[0])
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


# -----------------------------------------------


@app.route("/songs/<path:filename>")
def serve_song(filename):
    try:
        return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=False)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

# ---------------- Delete ------------------------


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
    return jsonify({"message": f"Class {class_item.name} and all related files deleted successfully"}), 200

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
    return jsonify({"message": f"Student {student.name} and related files deleted successfully"}), 200

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
    return jsonify({"message": f"Artist {artist.name} and all related files deleted successfully"}), 200

@app.route("/delete/song/<int:song_id>", methods=["DELETE"])
def delete_song(song_id):
    song = Song.query.get(song_id)
    if not song:
        return jsonify({"error": "Song not found"}), 404

    if song.file_path:
        file_path = os.path.join(DOWNLOAD_DIR, song.file_path)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

    db.session.delete(song)
    db.session.commit()
    return jsonify({"message": f"Song '{song.title}' and file deleted successfully"}), 200

@app.route("/delete/all", methods=["DELETE"])
def delete_all():
    try:
        for f in os.listdir(DOWNLOAD_DIR):
            path = os.path.join(DOWNLOAD_DIR, f)
            if os.path.isfile(path):
                os.remove(path)

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
        deleted_files = 0
        for f in os.listdir(DOWNLOAD_DIR):
            path = os.path.join(DOWNLOAD_DIR, f)
            if os.path.isfile(path):
                os.remove(path)
                deleted_files += 1

        return jsonify({"message": f"All downloads cleared ({deleted_files} files deleted)."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ----------------- Button Functons -----------------

@app.route("/download_student_songs/<int:student_id>", methods=["GET"])
@app.route("/download_student_songs/<int:student_id>", methods=["GET"])
def download_student_songs(student_id):
    print(f"Starting downloads for student {student_id}")

    songs = (
        Song.query.join(Artist)
        .filter(Artist.student_id == student_id)
        .filter(Song.file_path.is_(None))
        .all()
    )

    if not songs:
        return jsonify({"message": "No songs to download"}), 200

    socketio.emit("download_start", {"total": len(songs)})
    downloaded = 0
    failed = []

    def download_single(song):
        title = song.title
        link = song.link

        try:
            socketio.emit("download_status", {"song": title, "status": "starting"})

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s-%(id)s.%(ext)s"),
                "quiet": True,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }


            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(link, download=True)
                filename = os.path.splitext(ydl.prepare_filename(result))[0] + ".mp3"


            if filename:
                song.file_path = os.path.basename(filename)
                db.session.commit()

            socketio.emit("download_status", {"song": title, "status": "done"})
            return (title, True)

        except Exception as e:
            socketio.emit("download_status", {"song": title, "status": "failed", "error": str(e)})
            return (title, False)

    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(download_single, s): s for s in songs}

        for i, future in enumerate(as_completed(futures), start=1):
            title, success = future.result()
            if success:
                downloaded += 1
            else:
                failed.append(title)

            socketio.emit("download_progress", {
                "current": i,
                "total": len(songs),
                "last_song": title
            })

    socketio.emit("download_complete", {
        "downloaded": downloaded,
        "failed": failed
    })

    return jsonify({
        "message": f"Downloaded {downloaded} songs",
        "failed": failed
    }), 200






@app.route("/fetch_top_songs_all", methods=["GET"])
def fetch_top_songs_all():
    try:
        client_id = get_soundcloud_client_id()
        #print(f"Using SoundCloud client_id: {client_id[:6]}...")

        artists = Artist.query.all()
        added_count = 0
        results_summary = {}
        incomplete_artists = []

        for artist in artists:
            artist_name = artist.name
            #print(f"\nFetching top SoundCloud tracks for: {artist_name}")

            search_url = (
                f"https://api-v2.soundcloud.com/search/tracks"
                f"?q={artist_name}&client_id={client_id}&limit=5"
            )

            try:
                res = requests.get(search_url)
                data = res.json()
                tracks = data.get("collection", [])
            except Exception as e:
                print(f"API failed for {artist_name}: {e}")
                incomplete_artists.append(artist_name)
                continue

            if not tracks:
                print(f"No tracks found for {artist_name}")
                incomplete_artists.append(artist_name)
                continue

            valid_songs = []
            for t in tracks:
                title = t.get("title")
                url = t.get("permalink_url")
                if not title or not url:
                    continue

                valid_songs.append({"title": title, "link": url})
                existing = Song.query.filter_by(title=title, artist_id=artist.id).first()
                if not existing:
                    db.session.add(Song(title=title, link=url, artist_id=artist.id))
                    added_count += 1

            results_summary[artist_name] = valid_songs

        db.session.commit()
        return jsonify({
            "message": f"Added {added_count} SoundCloud songs total.",
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
    return send_from_directory(DOWNLOAD_DIR, filename)

@app.route("/list_songs")
def list_songs():
    try:
        files = [f for f in os.listdir(DOWNLOAD_DIR) if f.lower().endswith(".mp3")]
        return jsonify({"songs": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download_progress/<int:student_id>", methods=["GET"])
def download_progress(student_id):
    if not os.path.exists(DOWNLOAD_DIR):
        return jsonify([])
    downloaded_files = []
    for file in os.listdir(DOWNLOAD_DIR):
        if file.endswith(".mp3"):
            downloaded_files.append({
                "title": os.path.splitext(file)[0],
                "path": f"/downloads/{file}"
            })
    return jsonify(downloaded_files), 200

# -------------------- Main --------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, host="0.0.0.0", port=5050, debug=True, use_reloader=False)
