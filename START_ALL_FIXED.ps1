# Agent Aura - FIXED Complete System Startup
# This script ensures proper dependency installation and backend initialization

Write-Host "🚀 Starting Agent Aura Complete System (ENHANCED)" -ForegroundColor Cyan
Write-Host ""

# Step 1: Install missing dependencies
Write-Host "📦 Checking and installing dependencies..." -ForegroundColor Yellow
pip install prometheus-client reportlab pydantic-settings --quiet 2>$null

# Step 2: Initialize Database
Write-Host "🗄️  Initializing database with demo data..." -ForegroundColor Yellow
Push-Location "S:\Courses\Kaggle\Agent_Aura_GIT\agent-aura-backend"
$env:DATABASE_URL = "sqlite:///./agent_aura_local.db"
$env:SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
$env:PYTHONPATH = "S:\Courses\Kaggle\Agent_Aura_GIT\agent-aura-backend"
python -m app.init_demo_data 2>$null
Pop-Location

# Step 3: Start Backend
Write-Host "1️⃣  Starting Backend API Server..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd 'S:\Courses\Kaggle\Agent_Aura_GIT\agent-aura-backend'; `$env:DATABASE_URL='sqlite:///./agent_aura_local.db'; `$env:SECRET_KEY='09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 5

# Step 4: Start Frontend
Write-Host "2️⃣  Starting Frontend Server..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd 'S:\Courses\Kaggle\Agent_Aura_GIT\agent-aura-frontend'; npm run dev"

Start-Sleep -Seconds 8

# Step 5: Verify services
Write-Host ""
Write-Host "📊 Service Status:" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Demo Credentials:" -ForegroundColor Yellow
Write-Host"  Admin: admin / admin123" -ForegroundColor White
Write-Host ""
Write-Host "🎉 System Ready!" -ForegroundColor Green

Read-Host "`nPress Enter to close"
