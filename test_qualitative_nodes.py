"""
测试定性节点提取功能
"""
import asyncio
import sys
import os

# 添加 backend 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.node_sensing_service import NodeSensingService


async def test_qualitative_node():
    """测试定性节点的状态提取"""
    
    print("="*80)
    print("测试定性节点状态提取")
    print("="*80)
    
    # 初始化服务
    service = NodeSensingService()
    
    # 测试节点：地缘政治风险（定性）
    test_node = {
        "id": "n1",
        "label": "地缘政治风险",
        "type": "geopolitical_risk",  # 定性类型
        "description": "当前全球地缘政治紧张局势",
        "sensing_config": {
            "auto_queries": [
                "geopolitical risk middle east latest 2026",
                "global political tensions current 2026"
            ]
        }
    }
    
    print(f"\n[测试节点]")
    print(f"  - 标签: {test_node['label']}")
    print(f"  - 类型: {test_node['type']}")
    print(f"  - 查询: {test_node['sensing_config']['auto_queries']}")
    
    # 检查节点分类
    is_qualitative = service._is_qualitative_node(test_node['type'])
    print(f"\n[节点分类]")
    print(f"  - 是否为定性节点: {is_qualitative}")
    
    if is_qualitative:
        intensity_scale = service._get_intensity_scale(test_node['type'])
        print(f"  - 强度等级类型: {intensity_scale}")
        print(f"  - 可用等级: {service.intensity_levels.get(intensity_scale, [])}")
    
    # 执行状态提取
    print(f"\n[开始状态提取]")
    enriched_node = await service.enrich_node_state(test_node)
    
    # 输出结果
    print(f"\n[提取结果]")
    current_state = enriched_node.get('current_state', {})
    print(f"  - value: {current_state.get('value', 'N/A')}")
    print(f"  - intensity: {current_state.get('intensity', 'N/A')}")
    print(f"  - key_events: {current_state.get('key_events', [])}")
    print(f"  - trend: {current_state.get('trend', 'N/A')}")
    print(f"  - confidence: {current_state.get('confidence', 'N/A')}")
    print(f"  - sources: {len(current_state.get('sources', []))} 条")
    
    if current_state.get('value') != 'unknown':
        print(f"\n✅ 成功提取定性节点状态！")
    else:
        print(f"\n❌ 仍然返回 unknown")
    
    print("\n" + "="*80)


async def test_quantitative_node():
    """测试定量节点的状态提取（对比）"""
    
    print("\n" + "="*80)
    print("测试定量节点状态提取（对比）")
    print("="*80)
    
    # 初始化服务
    service = NodeSensingService()
    
    # 测试节点：美元指数（定量）
    test_node = {
        "id": "n2",
        "label": "美元指数",
        "type": "forex_rate",  # 定量类型
        "description": "美元相对其他主要货币的汇率指数",
        "sensing_config": {
            "auto_queries": [
                "US Dollar Index DXY current value 2026",
                "dollar index latest 2026"
            ]
        }
    }
    
    print(f"\n[测试节点]")
    print(f"  - 标签: {test_node['label']}")
    print(f"  - 类型: {test_node['type']}")
    
    # 检查节点分类
    is_qualitative = service._is_qualitative_node(test_node['type'])
    print(f"\n[节点分类]")
    print(f"  - 是否为定性节点: {is_qualitative}")
    
    # 执行状态提取
    print(f"\n[开始状态提取]")
    enriched_node = await service.enrich_node_state(test_node)
    
    # 输出结果
    print(f"\n[提取结果]")
    current_state = enriched_node.get('current_state', {})
    print(f"  - value: {current_state.get('value', 'N/A')}")
    print(f"  - trend: {current_state.get('trend', 'N/A')}")
    print(f"  - confidence: {current_state.get('confidence', 'N/A')}")
    print(f"  - sources: {len(current_state.get('sources', []))} 条")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    print("\n🧪 定性节点功能测试\n")
    
    # 测试定性节点
    asyncio.run(test_qualitative_node())
    
    # 测试定量节点（对比）
    asyncio.run(test_quantitative_node())
    
    print("\n✅ 测试完成！")
    print("\n提示：如果仍然返回 unknown，请检查：")
    print("  1. 后端服务是否已重启")
    print("  2. TAVILY_API_KEY 或 SERPER_API_KEY 是否配置")
    print("  3. 搜索引擎是否返回了有效结果")

