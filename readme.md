git clone https://github.com/coindxter/class_music.git \n
cd class_music/backend \n
python -m venv .venv \n
.venv\Scripts\activate \n
pip install -r requirements.txt \n

cd ../frontend \n
npm install \n
npm run build \n

cd ../backend \n
python app.py \n

http://localhost:5050