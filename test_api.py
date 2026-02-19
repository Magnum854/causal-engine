#!/usr/bin/env python3
"""
API 测试脚本 - 验证因果引擎是否正常工作
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("=" * 60)
    print("测试 1: 健康检查")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

def test_analyze_v2():
    """测试双阶段因果分析"""
    print("\n" + "=" * 60)
    print("测试 2: 双阶段因果分析 (analyze-v2)")
    print("=" * 60)
    
    payload = {
        "query": "黄金价格",
        "context": None,
        "max_depth": 3
    }
    
    try:
        print(f"发送请求: {json.dumps(payload, ensure_ascii=False)}")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze-v2",
            json=payload,
            timeout=60
        )
        
        elapsed = time.time() - start_time
        
        print(f"状态码: {response.status_code}")
        print(f"耗时: {elapsed:.2f} 秒")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n节点数: {len(data.get('nodes', []))}")
            print(f"边数: {len(data.get('edges', []))}")
            
            # 打印节点详情
            print("\n节点详情:")
            for node in data.get('nodes', [])[:3]:  # 只显示前3个
                print(f"  - {node.get('label')}: {node.get('type')}")
                if 'realtime_state' in node:
                    state = node['realtime_state']
                    print(f"    值: {state.get('latest_value', 'N/A')}")
                    print(f"    策略: {state.get('strategy_used', 'N/A')}")
                    print(f"    数据源: {len(state.get('sources', []))} 条")
            
            return True
        else:
            print(f"❌ 失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

def main():
    print("\n[START] 因果引擎 API 测试")
    print("=" * 60)
    
    results = []
    
    # 测试 1: 健康检查
    results.append(("健康检查", test_health()))
    
    # 测试 2: 因果分析
    results.append(("因果分析", test_analyze_v2()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n[SUCCESS] 所有测试通过！系统运行正常。")
    else:
        print("\n[WARNING] 部分测试失败，请检查日志。")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

