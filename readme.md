git clone https://github.com/coindxter/class_music.git

cd class_music/backend

python -m venv .venv

.\.venv\Scripts\Activate       # Windows

source venv/bin/activate     # Mac

pip install -r requirements.txt

cd ../frontend

npm install

npm run build

cd ../backend

python app.py

http://localhost:5050

[Notes](https://www.notion.so/GHENT-THING-28560bd3949080d48a9cf779fa7be68d?source=copy_link)