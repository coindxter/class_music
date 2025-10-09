Write-Host "Stopping Class Music Dashboard..."
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "Flask stopped!"
