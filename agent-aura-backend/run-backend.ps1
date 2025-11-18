# Agent Aura Backend Startup Script
Write-Host "Starting Agent Aura Backend..." -ForegroundColor Green

# Activate virtual environment
& S:/Courses/Kaggle/Agent_Aura_GIT/.venv/Scripts/Activate.ps1

# Set environment variables
$env:DATABASE_URL = "postgresql://agent_aura:agent_aura_password@localhost:5432/agent_aura_db"
$env:SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

# Change to backend directory
Set-Location S:/Courses/Kaggle/Agent_Aura_GIT/agent-aura-backend

Write-Host "Backend will start on http://localhost:8000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
