"""
节点自主感知功能测试脚本
快速验证 API 功能是否正常
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.node_sensing_service import NodeSensingService


async def test_single_node():
    """测试单个节点状态更新"""
    print("\n" + "="*80)
    print("测试 1: 单个节点状态更新")
    print("="*80)
    
    service = NodeSensingService()
    
    # 测试节点：美联储利率
    test_node = {
        "id": "n1",
        "label": "美联储利率",
        "type": "cause",
        "description": "美国联邦储备系统的基准利率",
        "sensing_config": {
            "auto_queries": [
                "美联储最新利率决议 2024",
                "Federal Reserve interest rate latest"
            ]
        }
    }
    
    print(f"\n输入节点: {test_node['label']}")
    print(f"搜索查询: {test_node['sensing_config']['auto_queries']}")
    
    # 执行状态更新
    enriched_node = await service.enrich_node_state(test_node)
    
    print(f"\n✅ 更新成功!")
    print(f"当前状态:")
    print(f"  - 值: {enriched_node['current_state']['value']}")
    print(f"  - 趋势: {enriched_node['current_state']['trend']}")
    print(f"  - 背景: {enriched_node['current_state']['narrative_context']}")
    print(f"  - 更新时间: {enriched_node.get('last_updated', 'N/A')}")


async def test_batch_nodes():
    """测试批量节点状态更新"""
    print("\n" + "="*80)
    print("测试 2: 批量节点状态更新（并发处理）")
    print("="*80)
    
    service = NodeSensingService()
    
    # 测试节点列表
    test_nodes = [
        {
            "id": "n1",
            "label": "黄金价格",
            "type": "intermediate",
            "sensing_config": {
                "auto_queries": [
                    "黄金价格最新行情",
                    "gold price today USD"
                ]
            }
        },
        {
            "id": "n2",
            "label": "原油价格",
            "type": "cause",
            "sensing_config": {
                "auto_queries": [
                    "布伦特原油价格今日",
                    "Brent crude oil price today"
                ]
            }
        },
        {
            "id": "n3",
            "label": "美元指数",
            "type": "cause",
            "sensing_config": {
                "auto_queries": [
                    "美元指数最新走势",
                    "US Dollar Index DXY latest"
                ]
            }
        }
    ]
    
    print(f"\n输入 {len(test_nodes)} 个节点:")
    for node in test_nodes:
        print(f"  - {node['label']}")
    
    # 批量处理
    enriched_nodes = await service.enrich_nodes_batch(test_nodes)
    
    print(f"\n✅ 批量更新成功!")
    for node in enriched_nodes:
        print(f"\n节点: {node['label']}")
        print(f"  - 值: {node['current_state']['value']}")
        print(f"  - 趋势: {node['current_state']['trend']}")
        print(f"  - 背景: {node['current_state']['narrative_context'][:50]}...")


async def test_missing_config():
    """测试缺少配置的节点（降级处理）"""
    print("\n" + "="*80)
    print("测试 3: 缺少配置的节点（降级处理）")
    print("="*80)
    
    service = NodeSensingService()
    
    # 缺少 sensing_config 的节点
    test_node = {
        "id": "n1",
        "label": "测试节点",
        "type": "cause"
        # 注意：没有 sensing_config
    }
    
    print(f"\n输入节点: {test_node['label']} (缺少 sensing_config)")
    
    enriched_node = await service.enrich_node_state(test_node)
    
    print(f"\n✅ 降级处理成功!")
    print(f"节点未被修改（跳过更新）")
    print(f"是否包含 current_state: {'current_state' in enriched_node}")


async def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("节点自主感知功能测试")
    print("="*80)
    
    # 检查环境变量
    print("\n检查环境变量配置...")
    
    required_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY"),
        "SERPER_API_KEY": os.getenv("SERPER_API_KEY")
    }
    
    for var, value in required_vars.items():
        status = "✅" if value else "❌"
        print(f"  {status} {var}: {'已配置' if value else '未配置'}")
    
    if not required_vars["OPENAI_API_KEY"]:
        print("\n❌ 错误: OPENAI_API_KEY 未配置，无法继续测试")
        return
    
    if not required_vars["TAVILY_API_KEY"] and not required_vars["SERPER_API_KEY"]:
        print("\n⚠️  警告: 搜索引擎 API 未配置，测试可能失败")
        print("   请配置 TAVILY_API_KEY 或 SERPER_API_KEY")
        return
    
    try:
        # 执行测试
        await test_single_node()
        await test_batch_nodes()
        await test_missing_config()
        
        print("\n" + "="*80)
        print("✅ 所有测试通过!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())

