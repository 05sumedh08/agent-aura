# Safe Git Commit Script for Agent Aura
# This script helps you commit only safe files (no secrets)

Write-Host "`n🔒 Agent Aura - Safe Commit Helper" -ForegroundColor Cyan
Write-Host "====================================`n" -ForegroundColor Cyan

# Step 1: Verify no secrets
Write-Host "Step 1: Checking for secrets..." -ForegroundColor Yellow
$secrets = git grep -l "AIzaSy" -- "*.py" "*.ts" "*.tsx" "*.js" 2>$null
if ($secrets) {
    Write-Host "❌ ERROR: Found potential API keys in source files!" -ForegroundColor Red
    Write-Host "Files with secrets:" -ForegroundColor Red
    $secrets | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    Write-Host "`n⚠️  Remove these secrets before committing!" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ No secrets found in source code`n" -ForegroundColor Green

# Step 2: Verify .env files are ignored
Write-Host "Step 2: Verifying .env files are protected..." -ForegroundColor Yellow
$envCheck = git check-ignore .env agent-aura-backend\.env .env.backup 2>$null
if ($envCheck) {
    Write-Host "✅ All .env files are properly ignored`n" -ForegroundColor Green
} else {
    Write-Host "⚠️  WARNING: Some .env files might not be ignored!" -ForegroundColor Yellow
}

# Step 3: Show what will be committed
Write-Host "Step 3: Safe files ready to commit:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  📝 .env.example" -ForegroundColor Green
Write-Host "  📝 agent-aura-backend/.env.example" -ForegroundColor Green
Write-Host "  📝 .gitignore" -ForegroundColor Green
Write-Host "  📝 SECURITY.md" -ForegroundColor Green
Write-Host "  📝 DOCUMENTATION_UPDATE.md" -ForegroundColor Green
Write-Host ""

# Step 4: Confirm
$confirm = Read-Host "Do you want to stage these files for commit? (y/n)"

if ($confirm -eq 'y' -or $confirm -eq 'Y') {
    Write-Host "`nStaging safe files..." -ForegroundColor Yellow
    
    git add .env.example
    git add agent-aura-backend/.env.example
    git add .gitignore
    git add SECURITY.md
    git add DOCUMENTATION_UPDATE.md
    
    Write-Host "✅ Files staged successfully`n" -ForegroundColor Green
    
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Review changes: git diff --cached" -ForegroundColor White
    Write-Host "  2. Commit: git commit -m 'docs: Add security documentation and environment templates'" -ForegroundColor White
    Write-Host "  3. Push: git push origin main`n" -ForegroundColor White
    
    # Show status
    Write-Host "Current git status:" -ForegroundColor Yellow
    git status --short
} else {
    Write-Host "`n❌ Cancelled. No files were staged." -ForegroundColor Red
}

Write-Host "`n✨ Remember: Your .env files with actual API keys are safe and will NOT be committed!" -ForegroundColor Green
Write-Host ""
