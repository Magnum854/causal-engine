"""
独立的工具函数：生成因果关系摘要
可以在任何地方导入使用
"""

from typing import Dict, Any, Optional, Union
from app.services.summary_service import SummaryGenerationService

# 创建全局服务实例
_summary_service = SummaryGenerationService()


async def generateCausalSummary(
    analysis_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    根据图结构动态生成文字简报（工具函数版本）
    
    【功能说明】
    - 自动计算图的复杂度（基于 edges 数量）
    - 简单场景（edges ≤ 2）：生成一句话核心总结
    - 复杂场景（edges > 2）：生成结构化分析报告
    - 完全容错：失败时不影响原始数据，summary 字段为 null
    
    【参数】
    analysis_result: Dict[str, Any]
        包含以下字段的字典：
        - nodes: List[Dict] - 节点数组
        - edges: List[Dict] - 边数组
        - explanation: str - 文字解释
        - 其他可选字段
    
    【返回值】
    Dict[str, Any]
        在原始 analysis_result 基础上添加 summary 字段：
        {
            ...原始字段,
            "summary": {
                "type": "simple" | "complex",
                "complexity": "simple" | "complex",
                "content": str | Dict  // 简单场景为字符串，复杂场景为结构化对象
            } | null  // 失败时为 null
        }
    
    【使用示例】
    ```python
    from app.utils.summary_utils import generateCausalSummary
    
    # 假设已经有了因果分析结果
    result = {
        "nodes": [...],
        "edges": [...],
        "explanation": "..."
    }
    
    # 生成摘要
    result_with_summary = await generateCausalSummary(result)
    
    # 检查摘要
    if result_with_summary["summary"]:
        if result_with_summary["summary"]["type"] == "simple":
            print("一句话总结:", result_with_summary["summary"]["content"])
        else:
            print("结构化分析:", result_with_summary["summary"]["content"])
    ```
    
    【复杂度判断逻辑】
    - edges.length <= 2 → simple（简单场景）
    - edges.length > 2 → complex（复杂场景）
    
    【Prompt 路由策略】
    
    Simple 场景 Prompt:
    "你是一个宏观分析师。请根据以下提取出的因果链数据，用【一句话】总结核心结论
    （直接说明某事件对某资产的利好/利空影响），不需要任何多余解释。"
    
    Complex 场景 Prompt:
    "你是一个首席宏观策略师。请根据以下因果关系图数据，写一份结构化简报。
    必须包含两个模块：
    1. 核心传导路径（描述事件如何一步步影响资产）
    2. 资产映射与策略
    请以 JSON 格式输出。"
    
    【容错机制】
    - 超时（30秒）→ summary = null
    - API 调用失败 → summary = null
    - JSON 解析失败 → summary = null
    - 任何异常 → summary = null
    - 保证原始数据完整返回
    """
    return await _summary_service.generate_causal_summary_safe(analysis_result)


# 同步包装版本（如果需要在非异步环境中使用）
def generateCausalSummarySync(
    analysis_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    同步版本的摘要生成（需要在异步环境中运行）
    
    注意：这个函数实际上仍然需要异步环境，
    只是提供了一个同步的接口签名。
    如果在纯同步环境中使用，需要使用 asyncio.run()
    """
    import asyncio
    
    try:
        # 尝试获取当前事件循环
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果已经在异步环境中，抛出错误
            raise RuntimeError(
                "不能在已运行的事件循环中调用同步版本，请使用 await generateCausalSummary()"
            )
        return loop.run_until_complete(generateCausalSummary(analysis_result))
    except RuntimeError:
        # 创建新的事件循环
        return asyncio.run(generateCausalSummary(analysis_result))


# 导出便捷函数
__all__ = [
    'generateCausalSummary',
    'generateCausalSummarySync',
]








