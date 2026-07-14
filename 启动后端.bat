@echo off
chcp 65001 >nul
echo ============================================================
echo 因果引擎后端 - 快速启动
echo ============================================================
echo.

cd /d "%~dp0backend"

echo [1/3] 检查环境变量配置...
if not exist .env (
    echo [ERROR] .env 文件不存在！
    echo 请参考 .env.example 创建 .env 文件
    pause
    exit /b 1
)
echo [OK] .env 文件存在

echo.
echo [2/3] 测试后端模块...
python test_backend.py
if errorlevel 1 (
    echo [ERROR] 后端模块测试失败！
    pause
    exit /b 1
)

echo.
echo [3/3] 启动后端服务...
echo.
echo 服务地址: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo.

python main.py

pause









