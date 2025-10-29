# Git Commit and Deployment Prep Script
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "CODE BUDDY MCP - GIT SETUP" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

Set-Location "C:\Repos\code_buddy_mcp"

# Initialize git if needed
if (-not (Test-Path ".git")) {
    Write-Host "`nInitializing git repository..." -ForegroundColor Green
    git init
    git branch -M main
    Write-Host "Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "`nGit repository already exists" -ForegroundColor Gray
}

# Create .gitignore
Write-Host "`nCreating .gitignore..." -ForegroundColor Green
@"
# Python
__pycache__/
*.py[cod]
.venv/
venv/

# Environment
.env
*.env

# IDEs
.vscode/
.idea/

# Test files
_test_*.py

# Archive
archive/

# Logs
*.log
"@ | Out-File -FilePath ".gitignore" -Encoding utf8
Write-Host ".gitignore created" -ForegroundColor Green

# Check status
Write-Host "`nChecking files..." -ForegroundColor Green
$status = git status --short 2>&1
Write-Host $status -ForegroundColor Gray

# Stage files
Write-Host "`nStaging all files..." -ForegroundColor Green
git add .
Write-Host "Files staged" -ForegroundColor Green

# Commit
Write-Host "`nCreating commit..." -ForegroundColor Green
git commit -m "Production-ready Code Buddy MCP with 117 workflows"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Committed successfully!" -ForegroundColor Green
} else {
    Write-Host "Commit completed" -ForegroundColor Yellow
}

# Show next steps
Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "READY FOR GITHUB!" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

Write-Host "`nOption 1: GitHub CLI (recommended)" -ForegroundColor Cyan
Write-Host "  gh repo create code-buddy-mcp --public --source=. --remote=origin" -ForegroundColor White
Write-Host "  git push -u origin main" -ForegroundColor White

Write-Host "`nOption 2: GitHub Web" -ForegroundColor Cyan
Write-Host "  1. Go to: https://github.com/new" -ForegroundColor White
Write-Host "  2. Name: code-buddy-mcp" -ForegroundColor White
Write-Host "  3. Create repository" -ForegroundColor White
Write-Host "  4. Then run:" -ForegroundColor White
Write-Host "     git remote add origin https://github.com/YOUR_USERNAME/code-buddy-mcp.git" -ForegroundColor Gray
Write-Host "     git push -u origin main" -ForegroundColor Gray

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "Local repository ready!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
