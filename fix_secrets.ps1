# Fix Secret Scanning Issues
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "FIXING SECRET SCANNING ISSUES" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

Set-Location "C:\Repos\code_buddy_mcp"

Write-Host "`nReplacing example API keys in workflow files..." -ForegroundColor Green

# Fix third_party_api_integration.md
$file1 = "workflows/development/third_party_api_integration.md"
if (Test-Path $file1) {
    $content = Get-Content $file1 -Raw
    # Replace any Stripe test keys with placeholder
    $content = $content -replace 'sk_test_[a-zA-Z0-9]+', 'sk_test_YOUR_KEY_HERE'
    $content = $content -replace 'pk_test_[a-zA-Z0-9]+', 'pk_test_YOUR_KEY_HERE'
    $content | Set-Content $file1 -NoNewline
    Write-Host "  Fixed: $file1" -ForegroundColor Gray
}

# Fix git_history_cleanup_solo.md
$file2 = "workflows/security/git_history_cleanup_solo.md"
if (Test-Path $file2) {
    $content = Get-Content $file2 -Raw
    # Replace any Stripe keys with placeholder
    $content = $content -replace 'sk_live_[a-zA-Z0-9]+', 'sk_live_YOUR_KEY_HERE'
    $content = $content -replace 'sk_test_[a-zA-Z0-9]+', 'sk_test_YOUR_KEY_HERE'
    $content = $content -replace 'pk_live_[a-zA-Z0-9]+', 'pk_live_YOUR_KEY_HERE'
    $content = $content -replace 'pk_test_[a-zA-Z0-9]+', 'pk_test_YOUR_KEY_HERE'
    $content | Set-Content $file2 -NoNewline
    Write-Host "  Fixed: $file2" -ForegroundColor Gray
}

Write-Host "`nCommitting fixes..." -ForegroundColor Green
git add .
git commit --amend --no-edit

Write-Host "`nPushing to GitHub..." -ForegroundColor Green
git push -u origin main --force

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "DONE!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "`nYour repository is now on GitHub:" -ForegroundColor White
Write-Host "https://github.com/stotzc001/code-buddy-mcp" -ForegroundColor Cyan
