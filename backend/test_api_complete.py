# -*- coding: utf-8 -*-
"""
后端 API 完整测试脚本
测试所有关键接口是否正常工作
"""
import sys
import requests
import json

# 设置控制台编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查接口"""
    print("\n[测试 1] 健康检查接口")
    print("-" * 60)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_root():
    """测试根接口"""
    print("\n[测试 2] 根接口")
    print("-" * 60)
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_examples():
    """测试示例接口"""
    print("\n[测试 3] 示例接口")
    print("-" * 60)
    try:
        response = requests.get(f"{BASE_URL}/api/v1/examples", timeout=5)
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"示例查询数量: {len(data.get('examples', []))}")
        print(f"标的示例数量: {len(data.get('target_examples', []))}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_analyze():
    """测试因果分析接口"""
    print("\n[测试 4] 因果分析接口")
    print("-" * 60)
    try:
        payload = {
            "query": "美元指数上涨对黄金价格的影响",
            "context": None,
            "max_depth": 2
        }
        print(f"请求: {payload}")
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze",
            json=payload,
            timeout=30
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"节点数量: {len(data.get('nodes', []))}")
            print(f"边数量: {len(data.get('edges', []))}")
            print(f"解释: {data.get('explanation', '')[:100]}...")
            return True
        else:
            print(f"错误: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("=" * 60)
    print("后端 API 完整测试")
    print("=" * 60)
    
    results = []
    
    # 测试 1: 健康检查
    results.append(("健康检查", test_health()))
    
    # 测试 2: 根接口
    results.append(("根接口", test_root()))
    
    # 测试 3: 示例接口
    results.append(("示例接口", test_examples()))
    
    # 测试 4: 因果分析接口（需要 API Key）
    print("\n[提示] 因果分析接口需要有效的 OpenAI API Key")
    print("如果测试失败，请检查 .env 文件中的 OPENAI_API_KEY 配置")
    results.append(("因果分析", test_analyze()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n通过: {passed}/{total}")
    
    if passed == total:
        print("\n✓ 所有测试通过！后端服务运行正常。")
        return 0
    else:
        print(f"\n✗ {total - passed} 个测试失败，请检查错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())









