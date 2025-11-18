# Agent Aura - Quick Start Script
# This script helps you get started with the backend

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          🚀 AGENT AURA - BACKEND QUICKSTART 🚀                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "📦 Setting up Agent Aura Backend System..." -ForegroundColor Yellow
Write-Host ""

# Check Docker
Write-Host "[1/5] Checking Docker..." -ForegroundColor White
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "✅ Docker found" -ForegroundColor Green
} else {
    Write-Host "❌ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check Docker Compose
Write-Host "`n[2/5] Checking Docker Compose..." -ForegroundColor White
if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    Write-Host "✅ Docker Compose found" -ForegroundColor Green
} else {
    Write-Host "❌ Docker Compose not found. Please install Docker Compose." -ForegroundColor Red
    exit 1
}

# Check .env file
Write-Host "`n[3/5] Checking environment configuration..." -ForegroundColor White
if (Test-Path ".env") {
    Write-Host "✅ .env file exists" -ForegroundColor Green
    
    # Check for GEMINI_API_KEY
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "GEMINI_API_KEY=AIzaSy") {
        Write-Host "✅ GEMINI_API_KEY configured" -ForegroundColor Green
    } else {
        Write-Host "⚠️  GEMINI_API_KEY not set in .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  .env file not found. Copying from .env.template..." -ForegroundColor Yellow
    Copy-Item ".env.template" ".env"
    Write-Host "⚠️  Please edit .env and add your GEMINI_API_KEY" -ForegroundColor Yellow
}

# Start Docker services
Write-Host "`n[4/5] Starting Docker services..." -ForegroundColor White
Write-Host "This may take a few minutes on first run..." -ForegroundColor Gray

docker-compose -f docker-compose.full.yml up -d database

Write-Host "⏳ Waiting for database to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 10

Write-Host "✅ Database started" -ForegroundColor Green

# Start backend
Write-Host "`n[5/5] Starting backend service..." -ForegroundColor White

# Option 1: Docker (recommended)
$useDocker = Read-Host "`nDo you want to run backend in Docker? (Y/n)"
if ($useDocker -eq "" -or $useDocker -eq "Y" -or $useDocker -eq "y") {
    docker-compose -f docker-compose.full.yml up -d backend
    Write-Host "`n✅ Backend started in Docker" -ForegroundColor Green
    Write-Host "📡 API available at: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "📖 API Docs at: http://localhost:8000/docs" -ForegroundColor Cyan
} else {
    Write-Host "`nStarting backend locally..." -ForegroundColor Gray
    Write-Host "Run this command in another terminal:" -ForegroundColor Yellow
    Write-Host "  cd agent-aura-backend" -ForegroundColor White
    Write-Host "  pip install -r requirements.txt" -ForegroundColor White
    Write-Host "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
}

# Summary
Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                     ✅ SETUP COMPLETE!                        ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "🎉 Agent Aura Backend is ready!`n" -ForegroundColor White

Write-Host "Access the system:" -ForegroundColor Yellow
Write-Host "  📡 Backend API:   http://localhost:8000" -ForegroundColor White
Write-Host "  📖 API Docs:      http://localhost:8000/docs" -ForegroundColor White
Write-Host "  🗄️  Database:      localhost:5432" -ForegroundColor White

Write-Host "`nUseful commands:" -ForegroundColor Yellow
Write-Host "  View logs:        docker-compose -f docker-compose.full.yml logs -f" -ForegroundColor White
Write-Host "  Stop services:    docker-compose -f docker-compose.full.yml down" -ForegroundColor White
Write-Host "  Restart:          docker-compose -f docker-compose.full.yml restart backend" -ForegroundColor White

Write-Host "`n📚 Next steps:" -ForegroundColor Yellow
Write-Host "  1. Visit http://localhost:8000/docs to explore the API" -ForegroundColor White
Write-Host "  2. Test the /health endpoint" -ForegroundColor White
Write-Host "  3. Read PRODUCTION_README.md for full documentation" -ForegroundColor White
Write-Host "  4. Build the frontend (agent-aura-frontend) next!" -ForegroundColor White

Write-Host "`n🚀 Ready to build amazing AI agents!`n" -ForegroundColor Green
