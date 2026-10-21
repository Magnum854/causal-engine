@echo off
chcp 65001 >nul
echo ============================================================
echo 因果引擎 - 完整测试套件
echo ============================================================
echo.

cd /d "%~dp0backend"

echo [测试 1/3] 模块导入测试
echo ------------------------------------------------------------
python test_backend.py
if errorlevel 1 (
    echo [FAIL] 模块导入测试失败
    pause
    exit /b 1
)
echo [OK] 模块导入测试通过
echo.

echo [测试 2/3] QVeris 数据源接入测试
echo ------------------------------------------------------------
python test_qveris.py
echo.

echo [测试 3/3] API 接口测试
echo ------------------------------------------------------------
echo 注意: 此测试需要后端服务正在运行
echo 如果后端未启动，请先运行 启动后端.bat
echo.
choice /C YN /M "后端服务是否已启动"
if errorlevel 2 (
    echo 请先启动后端服务
    pause
    exit /b 0
)

python test_api_complete.py

echo.
echo ============================================================
echo 测试完成
echo ============================================================
pause









