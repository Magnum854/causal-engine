"""
摘要生成功能使用示例
展示如何在不同场景中使用 generateCausalSummary
"""

import asyncio
from app.utils.summary_utils import generateCausalSummary

# ============================================
# 示例 1: 基础使用
# ============================================

async def example_basic():
    """基础使用示例"""
    
    # 模拟一个简单的因果分析结果
    analysis_result = {
        "nodes": [
            {
                "id": "n1",
                "label": "美联储加息",
                "type": "cause",
                "description": "加息50个基点",
                "confidence": 0.95
            },
            {
                "id": "n2",
                "label": "美股下跌",
                "type": "effect",
                "description": "股市大幅下跌",
                "confidence": 0.9
            }
        ],
        "edges": [
            {
                "source": "n1",
                "target": "n2",
                "label": "直接导致",
                "strength": 0.9
            }
        ],
        "explanation": "美联储加息直接导致美股下跌"
    }
    
    # 生成摘要
    result = await generateCausalSummary(analysis_result)
    
    # 检查结果
    print("=" * 80)
    print("示例 1: 基础使用（简单场景）")
    print("=" * 80)
    print(f"节点数: {len(result['nodes'])}")
    print(f"边数: {len(result['edges'])}")
    
    if result.get("summary"):
        summary = result["summary"]
        print(f"\n摘要类型: {summary['type']}")
        print(f"复杂度: {summary['complexity']}")
        print(f"内容: {summary['content']}")
    else:
        print("\n摘要生成失败")


# ============================================
# 示例 2: 复杂场景
# ============================================

async def example_complex():
    """复杂场景示例"""
    
    # 模拟一个复杂的因果分析结果（多个节点和边）
    analysis_result = {
        "nodes": [
            {"id": "n1", "label": "俄乌冲突", "type": "cause"},
            {"id": "n2", "label": "油价飙升", "type": "intermediate"},
            {"id": "n3", "label": "通胀上升", "type": "intermediate"},
            {"id": "n4", "label": "央行加息", "type": "intermediate"},
            {"id": "n5", "label": "经济放缓", "type": "effect"}
        ],
        "edges": [
            {"source": "n1", "target": "n2", "strength": 0.95},
            {"source": "n2", "target": "n3", "strength": 0.9},
            {"source": "n3", "target": "n4", "strength": 0.85},
            {"source": "n4", "target": "n5", "strength": 0.8}
        ],
        "explanation": "俄乌冲突通过油价上涨推高通胀，迫使央行加息，最终导致经济放缓"
    }
    
    # 生成摘要
    result = await generateCausalSummary(analysis_result)
    
    print("\n" + "=" * 80)
    print("示例 2: 复杂场景")
    print("=" * 80)
    print(f"节点数: {len(result['nodes'])}")
    print(f"边数: {len(result['edges'])}")
    
    if result.get("summary"):
        summary = result["summary"]
        print(f"\n摘要类型: {summary['type']}")
        print(f"复杂度: {summary['complexity']}")
        
        if summary['type'] == 'complex':
            import json
            print("\n结构化分析:")
            print(json.dumps(summary['content'], indent=2, ensure_ascii=False))
        else:
            print(f"内容: {summary['content']}")
    else:
        print("\n摘要生成失败")


# ============================================
# 示例 3: 在 API 路由中使用
# ============================================

"""
from fastapi import APIRouter
from app.utils.summary_utils import generateCausalSummary

router = APIRouter()

@router.post("/analyze-with-summary")
async def analyze_with_summary(request: AnalysisRequest):
    # 1. 先进行因果分析
    analysis_result = await some_analysis_service.analyze(request.text)
    
    # 2. 生成摘要
    result_with_summary = await generateCausalSummary(analysis_result)
    
    # 3. 返回结果
    return result_with_summary
"""


# ============================================
# 示例 4: 批量处理
# ============================================

async def example_batch():
    """批量处理多个分析结果"""
    
    # 模拟多个分析结果
    results = [
        {
            "nodes": [{"id": "n1", "label": "事件A", "type": "cause"}],
            "edges": [],
            "explanation": "简单事件"
        },
        {
            "nodes": [
                {"id": "n1", "label": "事件B", "type": "cause"},
                {"id": "n2", "label": "结果B", "type": "effect"}
            ],
            "edges": [{"source": "n1", "target": "n2"}],
            "explanation": "简单因果"
        },
        {
            "nodes": [
                {"id": "n1", "label": "事件C", "type": "cause"},
                {"id": "n2", "label": "中间C", "type": "intermediate"},
                {"id": "n3", "label": "结果C", "type": "effect"}
            ],
            "edges": [
                {"source": "n1", "target": "n2"},
                {"source": "n2", "target": "n3"},
                {"source": "n1", "target": "n3"}
            ],
            "explanation": "复杂因果"
        }
    ]
    
    print("\n" + "=" * 80)
    print("示例 3: 批量处理")
    print("=" * 80)
    
    # 并发处理所有结果
    tasks = [generateCausalSummary(result) for result in results]
    results_with_summary = await asyncio.gather(*tasks)
    
    for i, result in enumerate(results_with_summary, 1):
        print(f"\n结果 {i}:")
        print(f"  边数: {len(result['edges'])}")
        if result.get("summary"):
            print(f"  摘要类型: {result['summary']['type']}")
        else:
            print(f"  摘要: 未生成")


# ============================================
# 示例 5: 错误处理
# ============================================

async def example_error_handling():
    """错误处理示例"""
    
    # 模拟一个可能导致错误的结果
    invalid_result = {
        "nodes": [],  # 空节点
        "edges": [],
        "explanation": "无效数据"
    }
    
    print("\n" + "=" * 80)
    print("示例 4: 错误处理")
    print("=" * 80)
    
    # 即使数据无效，函数也会安全返回
    result = await generateCausalSummary(invalid_result)
    
    print(f"原始数据保留: {result.get('explanation')}")
    print(f"摘要状态: {'生成成功' if result.get('summary') else '生成失败（返回 null）'}")


# ============================================
# 运行所有示例
# ============================================

async def run_all_examples():
    """运行所有示例"""
    await example_basic()
    await example_complex()
    await example_batch()
    await example_error_handling()


if __name__ == "__main__":
    # 运行示例
    asyncio.run(run_all_examples())








