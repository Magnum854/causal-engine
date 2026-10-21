# -*- coding: utf-8 -*-
import os
import sys

# 动态查找 backend 目录
dirs = os.listdir('X:\\')
target = [d for d in dirs if os.path.exists(os.path.join('X:\\', d, 'backend'))][0]
backend_path = os.path.join('X:\\', target, 'backend')
os.chdir(backend_path)
sys.path.insert(0, backend_path)

print("=" * 60)
print("测试后端服务")
print("当前目录:", os.getcwd())
print("=" * 60)

try:
    print("\n1. 测试基础库...")
    from fastapi import FastAPI
    from pydantic import BaseModel
    from openai import AsyncOpenAI
    print("   ✓ 基础库导入成功")
    
    print("\n2. 测试服务模块...")
    from app.services.enhanced_research_service import EnhancedTargetResearchService
    from app.services.causal_service import CausalService
    from app.services.node_sensing_service import NodeSensingService
    print("   ✓ 服务模块导入成功")
    
    print("\n3. 测试路由...")
    from app.api.causal_router import router
    print("   ✓ 路由导入成功")
    
    print("\n4. 测试主应用...")
    import main
    print("   ✓ 主应用导入成功")
    
    print("\n" + "=" * 60)
    print("所有模块导入成功！后端程序正常。")
    print("=" * 60)
    print("\n可以运行以下命令启动服务:")
    print("  python main.py")
    print("  或")
    print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)












