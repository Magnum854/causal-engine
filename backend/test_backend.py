# -*- coding: utf-8 -*-
"""测试后端服务是否正常"""
import os
import sys

# 设置控制台编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加当前目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("=" * 60)
print("测试后端服务模块导入")
print("=" * 60)

try:
    print("\n1. 测试 FastAPI...")
    from fastapi import FastAPI
    print("   [OK] FastAPI 导入成功")
    
    print("\n2. 测试 Pydantic...")
    from pydantic import BaseModel
    print("   [OK] Pydantic 导入成功")
    
    print("\n3. 测试 OpenAI...")
    from openai import AsyncOpenAI
    print("   [OK] OpenAI 导入成功")
    
    print("\n4. 测试服务模块...")
    from app.services.enhanced_research_service import EnhancedTargetResearchService
    print("   [OK] EnhancedTargetResearchService 导入成功")
    
    from app.services.causal_service import CausalService
    print("   [OK] CausalService 导入成功")
    
    from app.services.node_sensing_service import NodeSensingService
    print("   [OK] NodeSensingService 导入成功")
    
    print("\n5. 测试路由...")
    from app.api.causal_router import router
    print("   [OK] Router 导入成功")
    
    print("\n6. 测试主应用...")
    import main
    print("   [OK] Main 应用导入成功")
    
    print("\n" + "=" * 60)
    print("所有模块导入成功！后端程序正常。")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)




