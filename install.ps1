# Causal Engine - Install Script (PowerShell)
# Run as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Causal Engine - Installing Dependencies" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "WARNING: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "Some operations may fail. Please run PowerShell as Administrator." -ForegroundColor Yellow
    Write-Host ""
}

# Check Python
Write-Host "[1/4] Checking Python..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    Write-Host "OK: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ from https://www.python.org/downloads/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Check Node.js
Write-Host "[2/4] Checking Node.js..." -ForegroundColor Green
try {
    $nodeVersion = node --version 2>&1
    $npmVersion = npm --version 2>&1
    Write-Host "OK: Node $nodeVersion, npm $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js not found" -ForegroundColor Red
    Write-Host "Please install Node.js 18+ from https://nodejs.org/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Install backend dependencies
Write-Host "[3/4] Installing Python packages..." -ForegroundColor Green
Set-Location backend

if (-not (Test-Path "requirements.txt")) {
    Write-Host "ERROR: requirements.txt not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Installing Python packages (using python -m pip)..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install Python packages" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please try manually:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor Yellow
    Write-Host "  python -m pip install -r requirements.txt" -ForegroundColor Yellow
    Set-Location ..
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "OK: Python packages installed" -ForegroundColor Green
Set-Location ..
Write-Host ""

# Install frontend dependencies
Write-Host "[4/4] Installing Node.js packages..." -ForegroundColor Green
Set-Location frontend

if (-not (Test-Path "package.json")) {
    Write-Host "ERROR: package.json not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Clean up
Write-Host "Cleaning up old files..." -ForegroundColor Yellow
Remove-Item package-lock.json -ErrorAction SilentlyContinue
Remove-Item node_modules -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Installing Node.js packages (this may take a few minutes)..." -ForegroundColor Yellow
npm cache clean --force
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install Node.js packages" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please try manually:" -ForegroundColor Yellow
    Write-Host "  cd frontend" -ForegroundColor Yellow
    Write-Host "  npm install" -ForegroundColor Yellow
    Set-Location ..
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "OK: Node.js packages installed" -ForegroundColor Green
Set-Location ..
Write-Host ""

# Create .env file
Write-Host "[Config] Creating .env file..." -ForegroundColor Green
$envPath = "backend\.env"
if (-not (Test-Path $envPath)) {
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
    $envContent | Out-File -FilePath $envPath -Encoding UTF8
    Write-Host "OK: Config file created" -ForegroundColor Green
} else {
    Write-Host "OK: Config file exists" -ForegroundColor Green
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SUCCESS: Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next step: Run start.ps1" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"







