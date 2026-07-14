@echo off
chcp 65001 >nul
echo ========================================
echo 因果引擎后端服务启动脚本
echo ========================================

cd /d "%~dp0"

echo.
echo 检查依赖...
python -c "from fastapi import FastAPI; from app.services.enhanced_research_service import EnhancedTargetResearchService; print('✓ 依赖检查通过')" 2>nul
if errorlevel 1 (
    echo ❌ 依赖检查失败，请先安装依赖
    echo 运行: pip install fastapi uvicorn pydantic pydantic-settings python-dotenv openai httpx aiohttp duckduckgo-search yfinance python-multipart
    pause
    exit /b 1
)

echo.
echo 启动后端服务...
echo 访问地址: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.

python main.py












