# ==========================================
# 🚀 Start Class Music Full Stack Environment
# ==========================================

Write-Host "🔍 Checking Docker status..." -ForegroundColor Cyan

# 1. Start Docker Desktop if not running
$dockerStatus = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $dockerStatus) {
    Write-Host "🐳 Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Write-Host "⏳ Waiting for Docker to initialize..."
    Start-Sleep -Seconds 20
} else {
    Write-Host "✅ Docker Desktop already running." -ForegroundColor Green
}

# 2. Navigate to your project folder
Set-Location "C:\Users\owenc\python\class_music"

# 3. Start your containers fresh
Write-Host "⚙️  Starting containers..." -ForegroundColor Cyan
docker compose up --build
