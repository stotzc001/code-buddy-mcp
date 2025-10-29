# Test Code Buddy MCP Server
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "CODE BUDDY MCP - TESTS" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

$testsPassed = 0
$testsFailed = 0

# Test 1: Environment
Write-Host "`n[1/4] Checking environment..." -ForegroundColor Green
$result = & ".venv\Scripts\python.exe" "_test_env.py" 2>&1
if ($result -match "OK:PROVIDER=") {
    $provider = $result -replace ".*OK:PROVIDER=", ""
    Write-Host "  Provider: $provider" -ForegroundColor Gray
    $testsPassed++
} else {
    Write-Host "  FAILED" -ForegroundColor Red
    Write-Host $result -ForegroundColor Gray
    $testsFailed++
}

# Test 2: Database
Write-Host "`n[2/4] Testing database..." -ForegroundColor Green
$result = & ".venv\Scripts\python.exe" "_test_db.py" 2>&1
if ($result -match "OK") {
    Write-Host "  Connected" -ForegroundColor Gray
    $testsPassed++
} else {
    Write-Host "  FAILED" -ForegroundColor Red
    Write-Host $result -ForegroundColor Gray
    $testsFailed++
}

# Test 3: Workflows
Write-Host "`n[3/4] Checking workflows..." -ForegroundColor Green
$result = & ".venv\Scripts\python.exe" "_test_workflows.py" 2>&1
if ($result -match "OK:COUNT=") {
    $count = $result -replace ".*OK:COUNT=", ""
    Write-Host "  Found: $count workflows" -ForegroundColor Gray
    $testsPassed++
} else {
    Write-Host "  FAILED" -ForegroundColor Red
    Write-Host $result -ForegroundColor Gray
    $testsFailed++
}

# Test 4: Embeddings
Write-Host "`n[4/4] Testing embeddings..." -ForegroundColor Green
$result = & ".venv\Scripts\python.exe" "_test_embeddings.py" 2>&1
if ($result -match "OK:MODEL=") {
    $model = ($result -match "OK:MODEL=(.+):DIMS=(\d+)") | Out-Null
    if ($matches) {
        Write-Host "  Model: $($matches[1]) ($($matches[2]) dims)" -ForegroundColor Gray
    }
    $testsPassed++
} else {
    Write-Host "  FAILED" -ForegroundColor Red
    Write-Host $result -ForegroundColor Gray
    $testsFailed++
}

# Summary
Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "RESULTS: $testsPassed/4 passed" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Yellow" })
Write-Host "================================================================================" -ForegroundColor Cyan

if ($testsFailed -eq 0) {
    Write-Host "`nAll tests passed! Your MCP server is ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Test with MCP Inspector (recommended):" -ForegroundColor White
    Write-Host "   .venv\Scripts\python.exe -m fastmcp dev src/server.py" -ForegroundColor Gray
    Write-Host "   Then open: http://localhost:5173" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Or configure Claude Desktop:" -ForegroundColor White
    Write-Host "   See: DEPLOYMENT_CHECKLIST.md" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "`nPlease fix errors above" -ForegroundColor Red
    exit 1
}
