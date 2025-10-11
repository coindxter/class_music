# Clone the repository
git clone https://github.com/coindxter/class_music.git
cd class_music/backend

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt

# Build the frontend
cd ../frontend
npm install
npm run build

# Return to backend and run Flask
cd ../backend
python app.py
