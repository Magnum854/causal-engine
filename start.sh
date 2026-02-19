#!/bin/bash

# 因果推演引擎 - 一键启动脚本

echo "================================"
echo "因果推演引擎 - 一键启动"
echo "================================"
echo ""

# 检查是否在项目根目录
if [ ! -d "frontend" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    echo "   当前目录应该是: x:/因果引擎"
    exit 1
fi

echo "📍 当前目录: $(pwd)"
echo ""

# 启动后端
echo "================================"
echo "🚀 启动后端服务..."
echo "================================"

# 在后台启动后端
cd backend
python main.py &
BACKEND_PID=$!
cd ..

echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
echo "   访问地址: http://localhost:8000"
echo ""

# 等待 3 秒
sleep 3

# 启动前端
echo "================================"
echo "🎨 启动前端服务..."
echo "================================"

cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
echo "   访问地址: http://localhost:5173"
echo ""

echo "================================"
echo "✅ 启动完成！"
echo "================================"
echo ""
echo "📋 服务信息:"
echo "   后端 API: http://localhost:8000"
echo "   前端界面: http://localhost:5173"
echo "   API 文档: http://localhost:8000/docs"
echo ""
echo "💡 提示:"
echo "   - 按 Ctrl+C 停止所有服务"
echo "   - 首次运行前端需要先执行: cd frontend && npm install"
echo ""

# 等待用户中断
wait







