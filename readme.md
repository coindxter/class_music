🎵 Class Music Dashboard
------------------------

A full-stack web app for managing class playlists — students, artists, and songs — with automatic YouTube song fetching and downloading support.

### 📁 Project Structure

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   class_music/  │  ├── backend/  │   ├── app.py  │   ├── classdj.db  │   ├── requirements.txt  │   └── start.sh  │  ├── frontend/  │   ├── package.json  │   ├── vite.config.js  │   ├── src/  │   │   ├── App.jsx  │   │   ├── main.jsx  │   │   └── components/  │   │       └── AddForm.jsx  │   └── dist/  ← built React app  │  └── README.md   `

🚀 Features
-----------

*   🏫 Manage **Classes → Students → Artists → Songs** hierarchy
    
*   🎶 Automatically fetch **top 5 YouTube songs** per artist
    
*   💾 Store data locally in SQLite (classdj.db)
    
*   🧨 Safe delete confirmation for all delete actions
    
*   ⚙️ Modern **Flask + React (Vite)** stack
    
*   🎧 Uses **yt-dlp** and **ffmpeg** for audio handling
    

🧰 Requirements
---------------

DependencyVersion (tested)Python3.9 – 3.12Node.js18 +npm8 +ffmpeginstalled globallySQLiteincluded with Python

⚙️ Backend Setup (Flask)
------------------------

1.  cd backend
    
2.  python -m venv venvsource venv/bin/activate # macOS/Linuxvenv\\Scripts\\activate # Windows
    
3.  pip install -r requirements.txtIf you don’t have a requirements.txt, generate one:pip install flask flask-cors flask-sqlalchemy yt-dlp youtube-search-pythonpip freeze > requirements.txt
    
4.  **Install ffmpeg**
    
    *   macOS: brew install ffmpeg
        
    *   Ubuntu: sudo apt install ffmpeg
        
    *   Windows: download from [https://ffmpeg.org](https://ffmpeg.org) and add to PATH
        
5.  python app.pyFlask will start at → [**http://localhost:5050**](http://localhost:5050)
    

💻 Frontend Setup (React + Vite)
--------------------------------

1.  cd frontend
    
2.  npm install
    
3.  npm run devOpen → [**http://localhost:5173**](http://localhost:5173)
    
4.  npm run buildThis creates a dist/ folder with static assets that Flask can serve.
    

🌐 Connecting Frontend + Backend
--------------------------------

Your Flask app in backend/app.py already serves the built React app with:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")   `

When you run npm run build, those files go into frontend/dist, and Flask will automatically serve them at [**http://localhost:5050**](http://localhost:5050).

🧩 Deployment Options
---------------------

### 🪶 Option 1: Deploy with Gunicorn + Nginx (Recommended)

1.  cd frontend && npm run build
    
2.  cd backendgunicorn -w 4 app:app
    
3.  Point Nginx to serve static files from frontend/dist/and proxy API calls (/add\_\*, /delete/\*, /fetch\_top\_songs\_all) to Flask.
    

### ☁️ Option 2: Render / Railway / Fly.io

These services can auto-detect Python + Node projects.

**Procfile:**

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   web: gunicorn app:app   `

**Build Commands:**

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt   `

🧾 API Endpoints
----------------

MethodEndpointDescriptionGET/classes\_fullGet all classes, students, artists, songsPOST/add\_classAdd new classPOST/add\_studentAdd new studentPOST/add\_artistAdd artist to studentPOST/add\_songAdd song to artistDELETE/delete/allDelete everythingGET/fetch\_top\_songs\_allFetch top 5 YouTube songs for each artist

🧠 Notes
--------

*   Each artist fetches top 5 verified songs using YouTube metadata filtering.
    
*   Songs are stored in SQLite (classdj.db).
    
*   Downloads are optional — the app stores URLs and titles instead of large audio files.
    
*   Make sure ffmpeg is installed if you later enable audio downloads.
    

🧑‍💻 Development Tips
----------------------

*   Always start backend **before** frontend.
    
*   Use console.log and Flask logs for debugging API calls.
    
*   const API\_BASE = "http://localhost:5050";in your App.jsx.
    

🏁 Example Workflow
-------------------

1.  Create a class
    
2.  Add a student
    
3.  Add an artist (e.g., “NF”)
    
4.  Click **🎶 Fetch Top Songs**
    
5.  View songs auto-populated for each artist
    

Would you like me to include a **requirements.txt and package.json snippet** too (so you can deploy it cleanly to Render or Railway)?