@echo off
chcp 65001 >nul 2>&1

echo ========================================
echo Causal Engine - Install Dependencies
echo ========================================
echo.

REM Check Python
echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Please install Python 3.9+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo OK: Python installed
echo.

REM Check Node.js
echo [2/4] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found
    echo Please install Node.js 18+
    echo Download: https://nodejs.org/
    pause
    exit /b 1
)
node --version
npm --version
echo OK: Node.js installed
echo.

REM Install backend dependencies
echo [3/4] Installing Python packages...
cd backend
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found
    pause
    exit /b 1
)

echo Installing...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python packages
    echo.
    echo Please try manually:
    echo   cd backend
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)
echo OK: Python packages installed
cd ..
echo.

REM Install frontend dependencies
echo [4/4] Installing Node.js packages...
cd frontend
if not exist "package.json" (
    echo ERROR: package.json not found
    pause
    exit /b 1
)

echo Installing... (this may take a few minutes)
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install Node.js packages
    echo.
    echo Please try manually:
    echo   cd frontend
    echo   npm install
    pause
    exit /b 1
)
echo OK: Node.js packages installed
cd ..
echo.

REM Create .env file
echo [Config] Creating .env file...
if not exist "backend\.env" (
    (
        echo # DeepSeek API Config
        echo OPENAI_API_KEY=sk-808aa93c9409413bbfcf66505a96de94
        echo OPENAI_BASE_URL=https://api.deepseek.com/v1
        echo OPENAI_MODEL=deepseek-chat
        echo.
        echo # Server Config
        echo HOST=0.0.0.0
        echo PORT=8000
        echo.
        echo # Search Engine
        echo SEARCH_ENGINE=duckduckgo
    ) > backend\.env
    echo OK: Config file created
) else (
    echo OK: Config file exists
)
echo.

echo ========================================
echo SUCCESS: Installation Complete!
echo ========================================
echo.
echo Next step: Run start.bat
echo.
pause
