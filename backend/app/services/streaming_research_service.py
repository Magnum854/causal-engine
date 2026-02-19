"""
流式标的研究服务
支持实时进度推送的标的研究 Pipeline
"""

from openai import AsyncOpenAI
import os
import json
import time
import asyncio
from typing import Dict, Any, List, AsyncGenerator
from app.services.search_service import SearchService

class StreamingTargetResearchService:
    """流式标的逆向推演与实时分析服务"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.model = os.getenv("OPENAI_MODEL", "deepseek-reasoner")
        self.search_service = SearchService()
    
    async def _send_progress(self, status: str, message: str, data: Any = None) -> str:
        """
        构建进度事件 JSON
        
        Args:
            status: 状态标识 (step1, step2, step3, success, error)
            message: 进度消息
            data: 可选的数据负载
            
        Returns:
            格式化的 JSON 字符串
        """
        event = {
            "status": status,
            "message": message,
            "timestamp": time.time()
        }
        
        if data is not None:
            event["data"] = data
        
        return json.dumps(event, ensure_ascii=False) + "\n"
    
    async def stream_research_target(self, target: str) -> AsyncGenerator[str, None]:
        """
        流式执行标的研究 Pipeline
        
        在每个关键步骤推送进度事件
        
        Args:
            target: 标的名称
            
        Yields:
            进度事件 JSON 字符串
        """
        pipeline_start = time.time()
        
        try:
            # 发送开始事件
            yield await self._send_progress(
                "start",
                f"开始分析标的: {target}"
            )
            
            # ============================================
            # 步骤 1: 逆向因子提取与关键词生成
            # ============================================
            yield await self._send_progress(
                "step1_start",
                "正在提取核心影响因子..."
            )
            
            step1_start = time.time()
            
            try:
                step1_result = await self._step1_extract_factors(target)
                factors = step1_result["factors"]
                search_queries = step1_result["search_queries"]
                
                step1_elapsed = time.time() - step1_start
                
                yield await self._send_progress(
                    "step1_complete",
                    f"因子提取完成 (耗时 {step1_elapsed:.1f}秒)",
                    {
                        "factors": factors,
                        "search_queries": search_queries,
                        "elapsed": step1_elapsed
                    }
                )
                
            except Exception as e:
                yield await self._send_progress(
                    "error",
                    f"因子提取失败: {str(e)}"
                )
                return
            
            # ============================================
            # 步骤 2: 并发联网搜索
            # ============================================
            yield await self._send_progress(
                "step2_start",
                f"正在搜索最新资讯 ({len(search_queries)} 个查询)..."
            )
            
            step2_start = time.time()
            
            try:
                context = await self._step2_perform_search(search_queries)
                
                step2_elapsed = time.time() - step2_start
                
                yield await self._send_progress(
                    "step2_complete",
                    f"搜索完成 (获取 {len(context)} 字符，耗时 {step2_elapsed:.1f}秒)",
                    {
                        "context_length": len(context),
                        "elapsed": step2_elapsed
                    }
                )
                
            except Exception as e:
                # 搜索失败不中断流程
                context = ""
                yield await self._send_progress(
                    "step2_warning",
                    f"搜索失败，将使用空上下文继续: {str(e)}"
                )
            
            # ============================================
            # 步骤 3: 综合分析与因果图生成
            # ============================================
            yield await self._send_progress(
                "step3_start",
                "正在生成因果关系图谱..."
            )
            
            step3_start = time.time()
            
            try:
                analysis_result = await self._step3_generate_analysis(
                    target,
                    context,
                    factors
                )
                
                step3_elapsed = time.time() - step3_start
                
                yield await self._send_progress(
                    "step3_complete",
                    f"图谱生成完成 ({len(analysis_result['nodes'])} 个节点，耗时 {step3_elapsed:.1f}秒)",
                    {
                        "nodes_count": len(analysis_result["nodes"]),
                        "edges_count": len(analysis_result["edges"]),
                        "elapsed": step3_elapsed
                    }
                )
                
            except Exception as e:
                yield await self._send_progress(
                    "error",
                    f"图谱生成失败: {str(e)}"
                )
                return
            
            # ============================================
            # 完成：发送最终结果
            # ============================================
            total_elapsed = time.time() - pipeline_start
            
            final_result = {
                **analysis_result,
                "metadata": {
                    "target": target,
                    "factors": factors,
                    "search_queries": search_queries,
                    "context_length": len(context),
                    "total_time": total_elapsed
                }
            }
            
            yield await self._send_progress(
                "success",
                f"分析完成！总耗时 {total_elapsed:.1f}秒",
                final_result
            )
            
        except Exception as e:
            # 捕获所有未处理的异常
            yield await self._send_progress(
                "error",
                f"Pipeline 执行失败: {str(e)}"
            )
    
    async def _step1_extract_factors(self, target: str) -> Dict[str, Any]:
        """步骤 1: 逆向因子提取"""
        
        system_prompt = """你是一个资深量化宏观研究员。用户会输入一个金融/商业标的，请分析影响该标的的最核心变量，并生成3到5个用于搜索引擎的精简 Query，以获取该标的最新动态。

【输出要求】
必须严格输出以下 JSON 格式：
{
    "factors": ["影响因子1", "影响因子2", "影响因子3"],
    "search_queries": ["精准搜索词1", "精准搜索词2", "精准搜索词3"]
}"""

        user_prompt = f"请分析以下标的：{target}\n\n请输出：1. 影响该标的的核心因子 2. 用于搜索最新动态的精准关键词"

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
        
        if "factors" not in result or "search_queries" not in result:
            raise ValueError("LLM 返回缺少必需字段")
        
        return result
    
    async def _step2_perform_search(self, search_queries: List[str]) -> str:
        """步骤 2: 并发搜索"""
        return await self.search_service.perform_search(search_queries)
    
    async def _step3_generate_analysis(
        self,
        target: str,
        context: str,
        factors: List[str]
    ) -> Dict[str, Any]:
        """步骤 3: 因果分析"""
        
        system_prompt = """你是一个因果逻辑引擎。请阅读以下实时搜索到的 Context，分析这些最新事件如何影响目标资产。请提取出事件、传导机制，并严格按照 AnalysisResult 接口输出包含 nodes, edges 和 explanation 的 JSON 图数据结构。

【输出格式】
{
    "nodes": [{"id": "n1", "label": "节点标签", "type": "cause|effect|intermediate", "description": "描述", "confidence": 0.9}],
    "edges": [{"source": "n1", "target": "n2", "label": "关系", "description": "说明", "strength": 0.85}],
    "explanation": "整体分析"
}"""

        factors_text = "、".join(factors) if factors else "未指定"
        user_prompt = f"""【目标资产】{target}
【核心影响因子】{factors_text}
【实时搜索上下文】{context if context else "（未获取到搜索结果）"}

请分析上述最新事件如何影响目标资产，构建完整的因果传导路径。"""

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
        
        if "nodes" not in result or "edges" not in result:
            raise ValueError("LLM 返回缺少必需字段")
        
        return result







