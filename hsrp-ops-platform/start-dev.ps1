$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host "HSRP Ops Platform - Starting backend + frontend" -ForegroundColor Cyan

if (-not (Test-Path "$Root\frontend\node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location "$Root\frontend"
    npm install
    Set-Location $Root
}

foreach ($port in 8000, 8080) {
    $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($conn) {
        Write-Host "Port $port is in use (PID $($conn.OwningProcess)). Stop that process first or dev may fail." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "  Frontend: http://localhost:8080" -ForegroundColor Green
Write-Host "  Backend:  http://localhost:8000/docs" -ForegroundColor Green
Write-Host "  Login:    http://localhost:8080/login" -ForegroundColor Green
Write-Host ""

npm run dev
