@echo off
REM 因果推演引擎 - 快速配置脚本 (Windows)

echo ================================
echo 因果推演引擎 - API 配置
echo ================================
echo.

REM 检查是否在 backend 目录
if not exist "requirements.txt" (
    echo ❌ 错误: 请在 backend 目录下运行此脚本
    echo    cd backend ^&^& setup.bat
    exit /b 1
)

REM 创建 .env 文件
echo 📝 创建 .env 配置文件...

(
echo # OpenAI API 配置（使用 DeepSeek^)
echo OPENAI_API_KEY=your_api_key_here
echo OPENAI_BASE_URL=https://api.deepseek.com/v1
echo OPENAI_MODEL=deepseek-chat
echo.
echo # 摘要生成使用的快速模型（可选^)
echo OPENAI_SUMMARY_MODEL=deepseek-chat
echo.
echo # 服务器配置
echo HOST=0.0.0.0
echo PORT=8000
echo.
echo # 搜索引擎配置
echo SEARCH_ENGINE=duckduckgo
) > .env

echo ✅ .env 文件创建成功
echo.

REM 检查 Python 版本
echo 🐍 检查 Python 版本...
python --version
echo.

REM 安装依赖
echo 📦 安装 Python 依赖...
pip install -r requirements.txt

echo.
echo 🔍 安装搜索引擎支持（DuckDuckGo）...
pip install duckduckgo-search

echo.
echo ================================
echo ✅ 配置完成！
echo ================================
echo.
echo 📋 配置信息:
echo    API Key: your_api_key_here
echo    Base URL: https://api.deepseek.com/v1
echo    模型: deepseek-chat
echo    搜索引擎: DuckDuckGo (免费)
echo.
echo 🚀 启动服务:
echo    python main.py
echo.
echo 📚 查看文档:
echo    type API_CONFIG.md
echo.

pause







