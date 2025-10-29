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
from googleapiclient.discovery import build


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

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
YT_API_KEY = os.getenv("YT_API_KEY")
youtube = build("youtube", "v3", developerKey=YT_API_KEY)

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

def get_lastfm_top_tracks(artist_name, limit=5):
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "artist.gettoptracks",
        "artist": artist_name,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": limit
    }
    res = requests.get(url, params=params).json()
    tracks = res.get("toptracks", {}).get("track", [])
    return [t["name"] for t in tracks]


#uses yt-dlp search funciton
def search_youtube_for_audio(artist, title, max_results=10):
    BLOCK_WORDS = ["live", "remix", "sped", "speed", "nightcore", "slowed", "cover", "performance"]
    TARGET_WORDS = ["lyrics", "audio", "hq", "full"]

    query = f"{artist} {title} lyrics audio"

    ydl_opts = {
        "quiet": True,
        "default_search": "ytsearch",
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            entries = results.get("entries", [])

        scored = []
        for e in entries:
            video_title = (e.get("title") or "").lower()
            if any(word in video_title for word in BLOCK_WORDS):
                continue

            score = 0
            if any(w in video_title for w in TARGET_WORDS):
                score += 3
            if "official" in video_title:
                score -= 3

            scored.append((score, e['id']))

        if not scored:
            return None

        best_id = max(scored, key=lambda x: x[0])[1]
        return f"https://www.youtube.com/watch?v={best_id}"

    except Exception as e:
        return None

#uses Youtube API
def search_youtube_lyrics(artist, title, max_results=10):
    print("in search youtube lyric fun")
    if not YT_API_KEY:
        return None

    query = f"{artist} {title} lyrics audio"

    banned_keywords = [
        "live", "cover", "remix", "sped", "slowed",
        "performance", "instrumental", "karaoke",
        "parody", "tribute", "reverb", "chipmunk"
    ]

    try:
        response = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=max_results,
            videoEmbeddable="true"
        ).execute()

        items = response.get("items", [])
        if not items:
            return None

        scored = []
        for item in items:
            video_id = item["id"]["videoId"]
            title_text = item["snippet"]["title"].lower()
            channel = item["snippet"]["channelTitle"].lower()

            if any(bad in title_text for bad in banned_keywords):
                continue

            score = 0
            if "lyric" in title_text:
                score += 3
            if "audio" in title_text:
                score += 2
            if "topic" in channel or "vevo" in channel:
                score += 3

            scored.append((score, video_id))

        if scored:
            best = max(scored, key=lambda x: x[0])[1]
            return f"https://www.youtube.com/watch?v={best}"

        return f"https://www.youtube.com/watch?v={items[0]['id']['videoId']}"

    except Exception as e:
        print("YouTube API failed:", e)
        return None


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


# add a way to individually add songs
#@app.route("/add_song", methods=["POST"])
#def add_song_auto():


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
        artists = Artist.query.all()
        added_count = 0
        results = {}
        missing_youtube = []

        for artist in artists:
            top_tracks = get_lastfm_top_tracks(artist.name, limit=5)

            if not top_tracks:
                results[artist.name] = "No top tracks found"
                continue

            results[artist.name] = []

            for title in top_tracks:
                existing = Song.query.filter_by(title=title, artist_id=artist.id).first()
                if existing:
                    results[artist.name].append({"title": title, "status": "exists"})
                    continue

                #primary search function using Youtube API    
                yt_link = search_youtube_lyrics(artist.name, title)

                if not yt_link:
                    #Fall back if Youtube API doesn't work
                    yt_link = search_youtube_for_audio(artist.name, title)


                new_song = Song(
                    title=title,
                    link=yt_link,
                    artist_id=artist.id,
                )
                db.session.add(new_song)
                added_count += 1

                results[artist.name].append({
                    "title": title,
                    "youtube": yt_link,
                    "status": "added" if yt_link else "no_youtube"
                })

        db.session.commit()

        return jsonify({
            "message": f"Added {added_count} YouTube lyric/audio songs",
            "youtube_missing": missing_youtube,
            "data": results
        }), 200

    except Exception as e:
        db.session.rollback()
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
