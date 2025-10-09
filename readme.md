🎵 **Class Music Dashboard**

A full-stack app to manage class music — add classes, students, artists, and automatically fetch top 5 YouTube songs per artist.

---

### 🧰 Requirements

* Python 3.9+
* Node.js 18+
* npm 8+
* ffmpeg (installed globally)

---

### ⚙️ Backend Setup (Flask)

1. Go to the backend folder

   ```
   cd backend
   ```

2. Create and activate a virtual environment

   ```
   python -m venv venv
   source venv/bin/activate       # macOS/Linux
   venv\Scripts\activate          # Windows
   ```

3. Install dependencies

   ```
   pip install -r requirements.txt
   ```

   If you don’t have a requirements file yet:

   ```
   pip install flask flask-cors flask-sqlalchemy yt-dlp youtube-search-python
   pip freeze > requirements.txt
   ```

4. Make sure ffmpeg is installed

   * macOS: `brew install ffmpeg`
   * Ubuntu: `sudo apt install ffmpeg`
   * Windows: download from [https://ffmpeg.org](https://ffmpeg.org) and add to PATH

5. Run the backend

   ```
   python app.py
   ```

   The backend runs at: **[http://localhost:5050](http://localhost:5050)**

---

### 💻 Frontend Setup (React + Vite)

1. Go to the frontend folder

   ```
   cd frontend
   ```

2. Install dependencies

   ```
   npm install
   ```

3. Start the development server

   ```
   npm run dev
   ```

   Then open **[http://localhost:5173](http://localhost:5173)** in your browser.

---

### 🌐 Run Both Together

* Start the backend first:

  ```
  cd backend
  python app.py
  ```

* Then, in another terminal, start the frontend:

  ```
  cd frontend
  npm run dev
  ```

Now visit **[http://localhost:5173](http://localhost:5173)** to use the app.
