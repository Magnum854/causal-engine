# Causal Engine - Start Script (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Causal Engine - Starting Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check directories
if (-not (Test-Path "backend")) {
    Write-Host "ERROR: backend directory not found" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path "frontend")) {
    Write-Host "ERROR: frontend directory not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check backend dependencies
Write-Host "[Check] Verifying backend..." -ForegroundColor Green
python -c "import fastapi" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Backend dependencies not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run: .\install.ps1" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "OK: Backend ready" -ForegroundColor Green
Write-Host ""

# Check frontend dependencies
Write-Host "[Check] Verifying frontend..." -ForegroundColor Green
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "ERROR: Frontend dependencies not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run: .\install.ps1" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "OK: Frontend ready" -ForegroundColor Green
Write-Host ""

# Check config file
if (-not (Test-Path "backend\.env")) {
    Write-Host "[Warning] Creating default .env file..." -ForegroundColor Yellow
    $envContent = @"
# DeepSeek API Config
OPENAI_API_KEY=sk-808aa93c9409413bbfcf66505a96de94
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat

# Server Config
HOST=0.0.0.0
PORT=8000

# Search Engine
SEARCH_ENGINE=duckduckgo
"@
    $envContent | Out-File -FilePath "backend\.env" -Encoding UTF8
    Write-Host "OK: Config created" -ForegroundColor Green
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Services..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start backend
Write-Host "[1/2] Starting Backend (FastAPI)..." -ForegroundColor Green
$backendPath = Join-Path (Get-Location) "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$backendPath'; python main.py" -WindowStyle Normal
Write-Host "OK: Backend started" -ForegroundColor Green
Write-Host "URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

# Wait for backend
Write-Host "[Wait] Backend starting..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start frontend
Write-Host "[2/2] Starting Frontend (Vite + React)..." -ForegroundColor Green
$frontendPath = Join-Path (Get-Location) "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$frontendPath'; npm run dev" -WindowStyle Normal
Write-Host "OK: Frontend started" -ForegroundColor Green
Write-Host "URL: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""

# Wait for frontend
Write-Host "[Wait] Frontend starting..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SUCCESS: Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tips:" -ForegroundColor Yellow
Write-Host "  1. Visit: http://localhost:5173" -ForegroundColor White
Write-Host "  2. Two PowerShell windows opened" -ForegroundColor White
Write-Host "  3. Close windows to stop services" -ForegroundColor White
Write-Host "  4. Press Ctrl+C to stop" -ForegroundColor White
Write-Host ""

# Open browser
Write-Host "[Launch] Opening browser..." -ForegroundColor Green
Start-Sleep -Seconds 2
Start-Process "http://localhost:5173"

Write-Host ""
Read-Host "Press Enter to close this window"







