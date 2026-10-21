#!/bin/bash

# 因果推演引擎 - 快速配置脚本

echo "================================"
echo "因果推演引擎 - API 配置"
echo "================================"
echo ""

# 检查是否在 backend 目录
if [ ! -f "requirements.txt" ]; then
    echo "❌ 错误: 请在 backend 目录下运行此脚本"
    echo "   cd backend && bash setup.sh"
    exit 1
fi

# 创建 .env 文件
echo "📝 创建 .env 配置文件..."

cat > .env << 'EOF'
# OpenAI API 配置（使用 DeepSeek）
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat

# 摘要生成使用的快速模型（可选）
OPENAI_SUMMARY_MODEL=deepseek-chat

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 搜索引擎配置
SEARCH_ENGINE=duckduckgo
EOF

echo "✅ .env 文件创建成功"
echo ""

# 检查 Python 版本
echo "🐍 检查 Python 版本..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "   Python 版本: $python_version"
echo ""

# 安装依赖
echo "📦 安装 Python 依赖..."
pip install -r requirements.txt

echo ""
echo "🔍 安装搜索引擎支持（DuckDuckGo）..."
pip install duckduckgo-search

echo ""
echo "================================"
echo "✅ 配置完成！"
echo "================================"
echo ""
echo "📋 配置信息:"
echo "   API Key: your_api_key_here"
echo "   Base URL: https://api.deepseek.com/v1"
echo "   模型: deepseek-chat"
echo "   搜索引擎: DuckDuckGo (免费)"
echo ""
echo "🚀 启动服务:"
echo "   python main.py"
echo ""
echo "📚 查看文档:"
echo "   cat API_CONFIG.md"
echo ""







