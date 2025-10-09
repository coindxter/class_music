Write-Host "Starting Class Music Dashboard..."

cd backend
Write-Host "Activating virtual environment..."
venv\Scripts\activate

Write-Host "Starting Flask backend + frontend..."
python app.py
