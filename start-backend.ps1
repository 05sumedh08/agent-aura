# Quick Start Backend Script
# Starts the FastAPI backend with PostgreSQL

Write-Host "🚀 Starting Agent Aura Backend..." -ForegroundColor Cyan

# Set environment variables
$env:DATABASE_URL = "postgresql://agent_aura:agent_aura_password@localhost:5432/agent_aura_db"
$env:SECRET_KEY = "your-secret-key-change-in-production-use-env-variable-min-32-characters-long"
$env:GEMINI_API_KEY = "dummy-key-for-testing"

# Activate virtual environment
& S:/Courses/Kaggle/Agent_Aura_GIT/.venv/Scripts/Activate.ps1

# Navigate to backend
Set-Location S:\Courses\Kaggle\Agent_Aura_GIT\agent-aura-backend

# Install psycopg2-binary using pre-built wheel (if available)
Write-Host "📦 Installing backend dependencies..." -ForegroundColor Yellow
pip install --only-binary :all: fastapi uvicorn sqlalchemy python-jose passlib python-dotenv pydantic starlette

# Start the backend
Write-Host "✨ Starting FastAPI server on http://localhost:8000" -ForegroundColor Green
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
