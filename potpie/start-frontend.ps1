# PowerShell script to start the frontend server

Write-Host "Starting Explain My Failure Frontend..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend will be available at: http://localhost:4173" -ForegroundColor Green
Write-Host "Make sure the backend is running on port 8000!" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

Set-Location frontend
python -m http.server 4173
