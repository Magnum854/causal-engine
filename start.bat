@echo off
chcp 65001 >nul 2>&1

title Causal Engine

echo ========================================
echo Causal Engine - Starting Services
echo ========================================
echo.

REM Check directories
if not exist "backend" (
    echo ERROR: backend directory not found
    echo Current directory: %CD%
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ERROR: frontend directory not found
    pause
    exit /b 1
)

REM Check backend dependencies
echo [Check] Verifying backend...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo ERROR: Backend dependencies not installed
    echo.
    echo Please run: install.bat
    echo Or manually: cd backend ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)
echo OK: Backend ready
echo.

REM Check frontend dependencies
echo [Check] Verifying frontend...
if not exist "frontend\node_modules" (
    echo ERROR: Frontend dependencies not installed
    echo.
    echo Please run: install.bat
    echo Or manually: cd frontend ^&^& npm install
    pause
    exit /b 1
)
echo OK: Frontend ready
echo.

REM Check config file
if not exist "backend\.env" (
    echo [Warning] Creating default .env file...
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
    echo OK: Config created
    echo.
)

echo ========================================
echo Starting Services...
echo ========================================
echo.

REM Start backend
echo [1/2] Starting Backend (FastAPI)...
start "Backend-FastAPI" /D "%CD%\backend" cmd /k "chcp 65001 >nul 2>&1 && python main.py"
echo OK: Backend started
echo URL: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.

REM Wait for backend
echo [Wait] Backend starting...
timeout /t 5 /nobreak >nul

REM Start frontend
echo [2/2] Starting Frontend (Vite + React)...
start "Frontend-Vite" /D "%CD%\frontend" cmd /k "chcp 65001 >nul 2>&1 && npm run dev"
echo OK: Frontend started
echo URL: http://localhost:5173
echo.

REM Wait for frontend
echo [Wait] Frontend starting...
timeout /t 3 /nobreak >nul

echo ========================================
echo SUCCESS: Services Started!
echo ========================================
echo.
echo Service URLs:
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo Tips:
echo   1. Visit: http://localhost:5173
echo   2. Two terminal windows opened
echo   3. Close windows to stop services
echo   4. Press Ctrl+C to stop
echo.

REM Open browser
echo [Launch] Opening browser...
timeout /t 2 /nobreak >nul
start http://localhost:5173

echo.
echo Press any key to close this window...
pause >nul
