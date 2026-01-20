# PowerShell script to start the backend server
# Make sure you've set OPENROUTER_API_KEY in backend/.env first!

Write-Host "Starting Explain My Failure Backend..." -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "ERROR: backend\.env file not found!" -ForegroundColor Red
    Write-Host "Please create it with your OPENROUTER_API_KEY" -ForegroundColor Yellow
    exit 1
}

# Check if API key is set
$envContent = Get-Content "backend\.env" -Raw
if ($envContent -match "your_key_here") {
    Write-Host "WARNING: You need to replace 'your_key_here' with your actual OpenRouter API key!" -ForegroundColor Yellow
    Write-Host ""
}

# Navigate to backend and start server
Set-Location backend
Write-Host "Starting uvicorn server on http://0.0.0.0:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
