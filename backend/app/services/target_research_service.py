"""
标的研究服务
实现逆向因子提取、联网搜索和因果分析的完整 Pipeline
"""

from openai import AsyncOpenAI
import os
import json
import time
from typing import Dict, Any, List, Optional
from app.services.search_service import SearchService
from app.prompts.system_prompts import NEWS_CAUSALITY_EXTRACTION_PROMPT

class TargetResearchService:
    """标的逆向推演与实时分析服务"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.model = os.getenv("OPENAI_MODEL", "deepseek-reasoner")
        self.search_service = SearchService()
    
    async def step1_extract_factors_and_queries(self, target: str) -> Dict[str, Any]:
        """
        第一步：逆向因子提取与关键词生成
        
        Args:
            target: 标的名称（如"中证1000指数"）
            
        Returns:
            {
                "factors": ["因子1", "因子2", ...],
                "search_queries": ["查询1", "查询2", ...]
            }
        """
        print(f"\n[步骤 1] 开始逆向因子提取: {target}")
        start_time = time.time()
        
        system_prompt = """你是一个资深量化宏观研究员。用户会输入一个金融/商业标的，请分析影响该标的的最核心变量，并生成3到5个用于搜索引擎的精简 Query，以获取该标的最新动态。

【输出要求】
必须严格输出以下 JSON 格式：
{
    "factors": [
        "影响因子1",
        "影响因子2",
        "影响因子3"
    ],
    "search_queries": [
        "精准搜索词1",
        "精准搜索词2",
        "精准搜索词3"
    ]
}

【分析原则】
1. factors: 列出3-5个影响该标的的核心宏观/微观变量
2. search_queries: 生成3-5个适合搜索引擎的关键词组合，用于获取最新动态
3. 搜索词要精准、时效性强，避免过于宽泛
4. 考虑政策、市场、行业、技术等多个维度"""

        user_prompt = f"""请分析以下标的：

【标的】{target}

请输出：
1. 影响该标的的核心因子
2. 用于搜索最新动态的精准关键词"""

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
            
            # 验证必需字段
            if "factors" not in result or "search_queries" not in result:
                raise ValueError("LLM 返回缺少必需字段")
            
            elapsed = time.time() - start_time
            print(f"[步骤 1] 完成，耗时: {elapsed:.2f}秒")
            print(f"  - 提取因子: {len(result['factors'])} 个")
            print(f"  - 生成查询: {len(result['search_queries'])} 个")
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"[步骤 1] 失败，耗时: {elapsed:.2f}秒")
            raise Exception(f"因子提取失败: {str(e)}")
    
    async def step2_perform_search(self, search_queries: List[str]) -> str:
        """
        第二步：并发联网搜索
        
        Args:
            search_queries: 搜索关键词列表
            
        Returns:
            合并后的搜索上下文文本
        """
        print(f"\n[步骤 2] 开始并发搜索")
        start_time = time.time()
        
        try:
            # 使用搜索服务并发执行搜索
            context = await self.search_service.perform_search(search_queries)
            
            elapsed = time.time() - start_time
            print(f"[步骤 2] 完成，耗时: {elapsed:.2f}秒")
            print(f"  - 获取上下文: {len(context)} 字符")
            
            return context
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"[步骤 2] 失败，耗时: {elapsed:.2f}秒")
            # 搜索失败不应该中断整个流程
            print(f"  - 警告: 搜索失败，将使用空上下文继续分析")
            return ""
    
    async def step3_generate_causal_analysis(
        self, 
        target: str, 
        context: str,
        factors: List[str]
    ) -> Dict[str, Any]:
        """
        第三步：综合分析与因果图生成
        
        Args:
            target: 标的名称
            context: 搜索获取的上下文
            factors: 影响因子列表
            
        Returns:
            AnalysisResult 格式的因果图数据
        """
        print(f"\n[步骤 3] 开始综合分析与因果图生成")
        start_time = time.time()
        
        system_prompt = """你是一个因果逻辑引擎。请阅读以下实时搜索到的 Context，分析这些最新事件如何影响目标资产。请提取出事件、传导机制，并严格按照 AnalysisResult 接口输出包含 nodes, edges 和 explanation 的 JSON 图数据结构。

【输出格式】
{
    "nodes": [
        {
            "id": "n1",
            "label": "节点标签",
            "type": "cause|effect|intermediate|hypothesis|evidence",
            "description": "节点详细描述",
            "confidence": 0.9
        }
    ],
    "edges": [
        {
            "source": "n1",
            "target": "n2",
            "label": "因果关系类型",
            "description": "因果机制说明",
            "strength": 0.85
        }
    ],
    "explanation": "整体因果关系的综合分析"
}

【分析要求】
1. 重点关注最新事件对目标资产的影响路径
2. 构建完整的因果传导链条
3. 标注每个因果关系的强度和置信度
4. 区分直接影响和间接影响
5. 考虑多条传导路径的交互作用"""

        # 构建用户提示词
        factors_text = "、".join(factors) if factors else "未指定"
        
        user_prompt = f"""【目标资产】
{target}

【核心影响因子】
{factors_text}

【实时搜索上下文】
{context if context else "（未获取到搜索结果，请基于已知信息分析）"}

请分析：
1. 上述最新事件如何影响目标资产 [{target}]
2. 构建完整的因果传导路径
3. 评估每个因果关系的强度
4. 输出标准的因果图 JSON 数据"""

        try:
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
            
            # 验证数据完整性
            if not isinstance(result["nodes"], list) or not isinstance(result["edges"], list):
                raise ValueError("nodes 和 edges 必须是数组")
            
            if len(result["nodes"]) == 0:
                raise ValueError("节点列表不能为空")
            
            # 验证节点引用
            node_ids = {node["id"] for node in result["nodes"]}
            for edge in result["edges"]:
                if edge["source"] not in node_ids or edge["target"] not in node_ids:
                    raise ValueError(f"边引用了不存在的节点")
            
            elapsed = time.time() - start_time
            print(f"[步骤 3] 完成，耗时: {elapsed:.2f}秒")
            print(f"  - 生成节点: {len(result['nodes'])} 个")
            print(f"  - 生成边: {len(result['edges'])} 条")
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"[步骤 3] 失败，耗时: {elapsed:.2f}秒")
            raise Exception(f"因果分析失败: {str(e)}")
    
    async def research_target(self, target: str) -> Dict[str, Any]:
        """
        完整的标的研究 Pipeline
        
        执行三步走流程：
        1. 逆向因子提取与关键词生成
        2. 并发联网搜索
        3. 综合分析与因果图生成
        
        Args:
            target: 标的名称
            
        Returns:
            完整的分析结果，包含因果图和元数据
        """
        print(f"\n{'='*80}")
        print(f"开始标的研究 Pipeline: {target}")
        print(f"{'='*80}")
        
        pipeline_start = time.time()
        
        try:
            # 第一步：逆向因子提取
            step1_result = await self.step1_extract_factors_and_queries(target)
            factors = step1_result["factors"]
            search_queries = step1_result["search_queries"]
            
            # 第二步：并发搜索
            context = await self.step2_perform_search(search_queries)
            
            # 第三步：因果分析
            analysis_result = await self.step3_generate_causal_analysis(
                target, 
                context,
                factors
            )
            
            # 组装最终结果
            final_result = {
                **analysis_result,
                "metadata": {
                    "target": target,
                    "factors": factors,
                    "search_queries": search_queries,
                    "context_length": len(context),
                    "total_time": time.time() - pipeline_start
                }
            }
            
            total_elapsed = time.time() - pipeline_start
            print(f"\n{'='*80}")
            print(f"Pipeline 完成，总耗时: {total_elapsed:.2f}秒")
            print(f"{'='*80}\n")
            
            return final_result
            
        except Exception as e:
            total_elapsed = time.time() - pipeline_start
            print(f"\n{'='*80}")
            print(f"Pipeline 失败，总耗时: {total_elapsed:.2f}秒")
            print(f"错误: {str(e)}")
            print(f"{'='*80}\n")
            raise








