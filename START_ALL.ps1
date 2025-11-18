# Agent Aura - Complete System Startup
Write-Host "🚀 Starting Agent Aura Complete System..." -ForegroundColor Cyan
Write-Host ""

# Check if ports are already in use
$portCheck = @{
    3000 = "Frontend"
    8000 = "Backend"
}

foreach ($port in $portCheck.Keys) {
    $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($conn) {
        Write-Host "⚠️  Port $port ($($portCheck[$port])) is already in use" -ForegroundColor Yellow
        $process = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "   Process: $($process.Name) (PID: $($process.Id))" -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Green
Write-Host ""

# Start Backend
Write-Host "1️⃣  Starting Backend API Server..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-File", "S:\Courses\Kaggle\Agent_Aura_GIT\agent-aura-backend\run-backend.ps1"
Start-Sleep -Seconds 5

# Start Frontend
Write-Host "2️⃣  Starting Frontend Server..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd S:\Courses\Kaggle\Agent_Aura_GIT\agent-aura-frontend; npm run dev"
Start-Sleep -Seconds 8

# Verify services
Write-Host ""
Write-Host "📊 Checking Service Status..." -ForegroundColor Cyan
Write-Host ""

$fe = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
$be = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
$db = Get-NetTCPConnection -LocalPort 5432 -State Listen -ErrorAction SilentlyContinue

if ($be) {
    Write-Host "✅ Backend API:  http://localhost:8000" -ForegroundColor Green
    Write-Host "   API Docs:     http://localhost:8000/docs" -ForegroundColor Gray
} else {
    Write-Host "❌ Backend API:  Failed to start" -ForegroundColor Red
}

if ($fe) {
    Write-Host "✅ Frontend:     http://localhost:3000" -ForegroundColor Green
    Write-Host "   Login:        http://localhost:3000/login" -ForegroundColor Gray
} else {
    Write-Host "❌ Frontend:     Failed to start" -ForegroundColor Red
}

if ($db) {
    Write-Host "✅ Database:     PostgreSQL on port 5432" -ForegroundColor Green
} else {
    Write-Host "⚠️  Database:     Not running (optional for demo)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 System Ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Demo Credentials:" -ForegroundColor Cyan
Write-Host "  Admin:   admin / admin123" -ForegroundColor White
Write-Host "  Teacher: teacher1 / teacher123" -ForegroundColor White
Write-Host "  Student: STU001 / student123" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to exit this status window" -ForegroundColor Gray
Write-Host "(Backend and Frontend will continue running in separate windows)" -ForegroundColor Gray

# Keep this window open
Read-Host "`nPress Enter to close this window"
