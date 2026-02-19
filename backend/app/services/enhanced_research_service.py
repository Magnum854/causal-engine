"""
增强型标的研究服务
实现"因果分析 + 自动状态感知"的完整闭环
"""

from openai import AsyncOpenAI
import os
import json
import time
from typing import Dict, Any, List, Optional
from app.services.search_service import SearchService
from app.services.node_sensing_service import NodeSensingService
from app.prompts.system_prompts import NEWS_CAUSALITY_EXTRACTION_PROMPT
import logging

logger = logging.getLogger(__name__)


class EnhancedTargetResearchService:
    """增强型标的研究服务 - 自动感知节点状态"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.model = os.getenv("OPENAI_MODEL", "deepseek-reasoner")
        self.search_service = SearchService()
        self.sensing_service = NodeSensingService()
    
    async def research_target_with_sensing(self, target: str) -> Dict[str, Any]:
        """
        完整的标的研究 Pipeline（带自动状态感知）
        
        工作流程：
        1. 逆向因子提取 → 生成因果图谱
        2. 自动为关键节点配置搜索查询
        3. 并发获取所有节点的实时状态
        4. 返回带有实时数据的完整因果图谱
        
        Args:
            target: 标的名称（如"黄金价格"）
            
        Returns:
            完整的分析结果，包含：
            - nodes: 因果图节点（每个节点包含 current_state）
            - edges: 因果图边
            - explanation: 综合分析
            - metadata: 元数据
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"开始增强型标的研究: {target}")
        logger.info(f"{'='*80}")
        
        pipeline_start = time.time()
        
        try:
            # ============================================
            # 步骤 1: 因果分析 - 识别影响因子
            # ============================================
            logger.info(f"\n[步骤 1] 开始因果分析，识别影响 {target} 的关键因子")
            step1_start = time.time()
            
            causal_graph = await self._analyze_causal_factors(target)
            
            step1_elapsed = time.time() - step1_start
            logger.info(f"[步骤 1] 完成，耗时: {step1_elapsed:.2f}秒")
            logger.info(f"  - 识别节点: {len(causal_graph['nodes'])} 个")
            logger.info(f"  - 识别关系: {len(causal_graph['edges'])} 条")
            
            # ============================================
            # 步骤 2: 自动配置搜索查询
            # ============================================
            logger.info(f"\n[步骤 2] 为关键节点自动配置搜索查询")
            step2_start = time.time()
            
            nodes_with_queries = await self._auto_configure_queries(
                causal_graph['nodes'],
                target
            )
            
            step2_elapsed = time.time() - step2_start
            logger.info(f"[步骤 2] 完成，耗时: {step2_elapsed:.2f}秒")
            logger.info(f"  - 配置查询的节点: {len(nodes_with_queries)} 个")
            
            # ============================================
            # 步骤 3: 并发获取节点实时状态
            # ============================================
            logger.info(f"\n[步骤 3] 并发获取所有节点的实时状态")
            step3_start = time.time()
            
            enriched_nodes = await self.sensing_service.enrich_nodes_batch(
                nodes_with_queries
            )
            
            step3_elapsed = time.time() - step3_start
            logger.info(f"[步骤 3] 完成，耗时: {step3_elapsed:.2f}秒")
            
            # 统计状态更新情况
            updated_count = sum(
                1 for node in enriched_nodes 
                if node.get('current_state', {}).get('value') != 'unknown'
            )
            logger.info(f"  - 成功更新状态: {updated_count}/{len(enriched_nodes)} 个节点")
            
            # ============================================
            # 步骤 4: 生成综合分析报告
            # ============================================
            logger.info(f"\n[步骤 4] 生成综合分析报告")
            step4_start = time.time()
            
            enhanced_explanation = await self._generate_enhanced_explanation(
                target=target,
                nodes=enriched_nodes,
                edges=causal_graph['edges'],
                original_explanation=causal_graph['explanation']
            )
            
            step4_elapsed = time.time() - step4_start
            logger.info(f"[步骤 4] 完成，耗时: {step4_elapsed:.2f}秒")
            
            # ============================================
            # 组装最终结果
            # ============================================
            total_elapsed = time.time() - pipeline_start
            
            final_result = {
                "nodes": enriched_nodes,
                "edges": causal_graph['edges'],
                "explanation": enhanced_explanation,
                "metadata": {
                    "target": target,
                    "total_nodes": len(enriched_nodes),
                    "nodes_with_state": updated_count,
                    "total_time": total_elapsed,
                    "pipeline_steps": {
                        "causal_analysis": step1_elapsed,
                        "query_configuration": step2_elapsed,
                        "state_sensing": step3_elapsed,
                        "report_generation": step4_elapsed
                    }
                }
            }
            
            logger.info(f"\n{'='*80}")
            logger.info(f"Pipeline 完成，总耗时: {total_elapsed:.2f}秒")
            logger.info(f"{'='*80}\n")
            
            return final_result
            
        except Exception as e:
            total_elapsed = time.time() - pipeline_start
            logger.error(f"\n{'='*80}")
            logger.error(f"Pipeline 失败，总耗时: {total_elapsed:.2f}秒")
            logger.error(f"错误: {str(e)}")
            logger.error(f"{'='*80}\n")
            raise
    
    async def _analyze_causal_factors(self, target: str) -> Dict[str, Any]:
        """
        步骤 1: 分析影响标的的因果因子
        
        使用 LLM 识别影响目标资产的关键因素，构建因果图谱
        """
        system_prompt = """你是一个资深的宏观经济分析师。请分析影响目标资产的核心因果因子，构建完整的因果传导链条。

【输出格式】
必须严格输出以下 JSON 格式：
{
    "nodes": [
        {
            "id": "n1",
            "label": "节点标签（如：美元指数）",
            "type": "cause|effect|intermediate",
            "description": "节点详细描述",
            "confidence": 0.9
        }
    ],
    "edges": [
        {
            "source": "n1",
            "target": "n2",
            "label": "因果关系类型",
            "description": "传导机制说明",
            "strength": 0.85
        }
    ],
    "explanation": "整体因果关系的综合分析"
}

【分析要求】
1. 识别 3-7 个核心影响因子（节点）
2. 构建完整的因果传导路径（边）
3. 区分直接影响和间接影响
4. 标注每个因果关系的强度和置信度
5. 节点 label 必须简洁明确（如"美元指数"、"美联储利率"、"地缘政治风险"）"""

        user_prompt = f"""【目标资产】
{target}

请分析：
1. 影响该资产的核心宏观/微观因子
2. 这些因子之间的因果传导路径
3. 每个因子对目标资产的影响机制

输出标准的因果图 JSON 数据。"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # 验证必需字段
        if "nodes" not in result or "edges" not in result:
            raise ValueError("LLM 返回缺少必需字段")
        
        return result
    
    async def _auto_configure_queries(
        self, 
        nodes: List[Dict[str, Any]], 
        target: str
    ) -> List[Dict[str, Any]]:
        """
        步骤 2: 自动为节点配置搜索查询
        
        使用 LLM 为每个节点生成精准的搜索关键词
        """
        logger.info(f"[查询配置] 开始为 {len(nodes)} 个节点配置搜索查询")
        
        system_prompt = """你是一个搜索查询优化专家。请为给定的经济/金融节点生成精准的搜索关键词。

【输出格式】
必须严格输出以下 JSON 格式：
{
    "queries": [
        "精准搜索词1（中文）",
        "精准搜索词2（英文）"
    ]
}

【查询要求】
1. 生成 2-3 个搜索查询
2. 包含中英文关键词
3. 添加时间限定词（如"2024"、"最新"、"latest"）
4. 查询要具体、可搜索，避免过于宽泛
5. 针对数值型指标，使用"价格"、"利率"、"指数"等明确词汇

【示例】
节点: "美元指数"
输出: {"queries": ["美元指数最新走势 2024", "US Dollar Index DXY latest"]}

节点: "美联储利率"
输出: {"queries": ["美联储利率决议 2024", "Federal Reserve interest rate latest"]}"""

        # 并发为所有节点生成查询
        async def generate_queries_for_node(node: Dict[str, Any]) -> Dict[str, Any]:
            node_label = node.get("label", "")
            node_description = node.get("description", "")
            
            user_prompt = f"""【节点信息】
标签: {node_label}
描述: {node_description}
目标资产: {target}

请生成该节点的搜索查询关键词。"""

            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content
                result = json.loads(content)
                
                # 注入 sensing_config
                node["sensing_config"] = {
                    "auto_queries": result.get("queries", [])
                }
                
                logger.info(f"[查询配置] 节点 '{node_label}' 配置完成: {len(result.get('queries', []))} 个查询")
                
            except Exception as e:
                logger.warning(f"[查询配置] 节点 '{node_label}' 配置失败: {str(e)}")
                # 降级：使用节点标签作为查询
                node["sensing_config"] = {
                    "auto_queries": [f"{node_label} 最新", f"{node_label} latest"]
                }
            
            return node
        
        # 并发处理所有节点
        import asyncio
        configured_nodes = await asyncio.gather(
            *[generate_queries_for_node(node) for node in nodes],
            return_exceptions=True
        )
        
        # 过滤异常结果
        valid_nodes = [
            node for node in configured_nodes 
            if not isinstance(node, Exception)
        ]
        
        return valid_nodes
    
    async def _generate_enhanced_explanation(
        self,
        target: str,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        original_explanation: str
    ) -> str:
        """
        步骤 4: 生成增强型综合分析报告
        
        结合因果关系和实时状态数据，生成深度分析报告
        """
        # 构建节点状态摘要
        node_states = []
        for node in nodes:
            label = node.get("label", "")
            state = node.get("current_state", {})
            value = state.get("value", "unknown")
            trend = state.get("trend", "stable")
            context = state.get("narrative_context", "")
            
            node_states.append(f"- {label}: {value} (趋势: {trend}) - {context}")
        
        node_states_text = "\n".join(node_states)
        
        system_prompt = """你是一个首席宏观策略分析师。请结合因果关系分析和实时数据，撰写深度分析报告。

【报告要求】
1. 综合因果传导路径和实时状态数据
2. 分析当前各因子的状态如何影响目标资产
3. 指出关键传导机制和风险点
4. 给出明确的趋势判断和策略建议
5. 语言专业、逻辑清晰、结论明确

【报告结构】
第一段：核心结论（一句话总结当前状态对目标资产的影响）
第二段：因果传导分析（详细说明各因子如何影响目标）
第三段：风险与机会（基于实时数据的判断）
第四段：策略建议（可操作的投资建议）"""

        user_prompt = f"""【目标资产】
{target}

【因果关系分析】
{original_explanation}

【实时状态数据】
{node_states_text}

请撰写综合分析报告。"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                max_tokens=2000
            )
            
            enhanced_explanation = response.choices[0].message.content
            return enhanced_explanation
            
        except Exception as e:
            logger.error(f"[报告生成] 失败: {str(e)}")
            # 降级：返回原始分析 + 状态摘要
            return f"{original_explanation}\n\n【实时状态】\n{node_states_text}"

