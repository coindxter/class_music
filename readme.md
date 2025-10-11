git clone https://github.com/coindxter/class_music.git \
cd class_music/backend \
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

cd ../frontend
npm install
npm run build

cd ../backend
python app.py

http://localhost:5050