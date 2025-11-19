# Agent Aura Demo Launcher
# Starts the demo server and opens the dashboard

Write-Host "🚀 Starting Agent Aura Demo..." -ForegroundColor Cyan

# Activate virtual environment
& ".\.venv\Scripts\Activate.ps1"

# Start the demo server in background
Write-Host "📊 Starting demo server on port 5001..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\Activate.ps1; python demo_server.py"

# Wait for server to start
Write-Host "⏳ Waiting for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Open the dashboard in default browser
Write-Host "🌐 Opening dashboard..." -ForegroundColor Green
Start-Process "dashboard.html"

Write-Host ""
Write-Host "✅ Agent Aura Demo is running!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Dashboard: file:///$PWD/dashboard.html" -ForegroundColor Cyan
Write-Host "🔌 API Server: http://localhost:5001" -ForegroundColor Cyan
Write-Host "📖 API Docs: http://localhost:5001/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C in the server window to stop" -ForegroundColor Yellow
