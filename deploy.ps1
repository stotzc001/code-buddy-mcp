# Code Buddy MCP - Quick Deploy Script
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "CODE BUDDY MCP - SETUP" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

Set-Location "C:\Repos\code_buddy_mcp"

# Step 1: Create .venv
Write-Host "`n[1/3] Creating virtual environment..." -ForegroundColor Green
if (Test-Path ".venv") {
    Write-Host "  Removing existing .venv..." -ForegroundColor Yellow
    Remove-Item -Path ".venv" -Recurse -Force
}

python -m venv .venv
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Created .venv" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Step 2: Install dependencies
Write-Host "`n[2/3] Installing dependencies..." -ForegroundColor Green
& ".venv\Scripts\python.exe" -m pip install --upgrade pip 2>&1 | Out-Null
$installOutput = & ".venv\Scripts\pip.exe" install -r requirements.txt 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Failed to install dependencies" -ForegroundColor Red
    Write-Host $installOutput -ForegroundColor Red
    exit 1
}
Write-Host "  Dependencies installed" -ForegroundColor Green

# Step 3: Test imports
Write-Host "`n[3/3] Testing imports..." -ForegroundColor Green
$testResult = & ".venv\Scripts\python.exe" "_test_imports.py" 2>&1
if ($testResult -match "OK") {
    Write-Host "  All imports successful" -ForegroundColor Green
} else {
    Write-Host "  Import test failed:" -ForegroundColor Red
    Write-Host $testResult -ForegroundColor Gray
    exit 1
}

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETE!" -ForegroundColor Yellow  
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Run: .\test_mcp.ps1" -ForegroundColor Cyan
Write-Host ""
