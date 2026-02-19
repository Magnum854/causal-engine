"""
双阶段因果分析服务 (Two-Pass Pipeline with Multi-Tool Router)
Pass 1: 生成因果图谱拓扑结构
Pass 2: 动态富化节点 + 数据溯源（使用多路由工具调用）
"""

from openai import AsyncOpenAI
import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from urllib.parse import urlparse

from app.services.multi_tool_router_service import MultiToolRouterService
from app.services.yahoo_finance_service import YahooFinanceService

logger = logging.getLogger(__name__)


class SearchService:
    """搜索引擎服务（用于新闻搜索）"""
    
    def __init__(self):
        # 强制重新加载环境变量（解决热重载缓存问题）
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.use_mock = not (self.tavily_api_key or self.serper_api_key)
        
        if self.use_mock:
            logger.warning("[搜索引擎] 未配置真实 API，将使用 Mock 模式")
        else:
            if self.tavily_api_key:
                logger.info("[搜索引擎] ✅ 使用 Tavily API")
            elif self.serper_api_key:
                logger.info("[搜索引擎] ✅ 使用 Serper API")
    
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """执行搜索"""
        if self.use_mock:
            return await self._mock_search(query)
        
        if self.tavily_api_key:
            return await self._tavily_search(query)
        elif self.serper_api_key:
            return await self._serper_search(query)
        
        return []
    
    async def _mock_search(self, query: str) -> List[Dict[str, Any]]:
        """Mock 搜索"""
        logger.info(f"[Mock Search] 模拟搜索: {query}")
        await asyncio.sleep(0.5)
        
        mock_results = [
            {
                "title": f"{query} - 最新数据报告",
                "url": "https://www.bloomberg.com/mock-article-1",
                "snippet": f"根据最新数据显示，{query}呈现稳定趋势..."
            },
            {
                "title": f"{query} - 市场分析",
                "url": "https://www.reuters.com/mock-article-2",
                "snippet": f"专家分析指出，{query}受多重因素影响..."
            }
        ]
        
        logger.info(f"[Mock Search] 返回 {len(mock_results)} 条模拟结果")
        return mock_results
    
    async def _tavily_search(self, query: str) -> List[Dict[str, Any]]:
        """Tavily 搜索"""
        # TODO: 实现真实 Tavily API 调用
        return await self._mock_search(query)
    
    async def _serper_search(self, query: str) -> List[Dict[str, Any]]:
        """Serper 搜索"""
        # TODO: 实现真实 Serper API 调用
        return await self._mock_search(query)


class TwoPassCausalService:
    """双阶段因果分析服务（集成多路由工具调用）"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.model = os.getenv("OPENAI_MODEL", "deepseek-reasoner")
        
        # 初始化搜索服务
        self.search_service = SearchService()
        
        # 初始化多路由服务
        self.router = MultiToolRouterService(search_service=self.search_service)
        
        # 初始化 Yahoo Finance 直连服务
        self.yahoo_finance = YahooFinanceService()
        
        logger.info("[TwoPassCausal] 初始化完成（集成多路由工具调用 + Yahoo Finance 直连）")
    
    async def analyze_two_pass(
        self, 
        query: str, 
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        双阶段因果分析主流程
        
        Args:
            query: 分析查询（如"黄金价格的影响因素"）
            context: 可选的背景信息
            
        Returns:
            完整的因果图谱（包含实时状态和数据溯源）
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"[双阶段分析] 开始分析: {query}")
        logger.info(f"{'='*80}")
        
        # ============================================
        # Pass 1: 生成拓扑结构
        # ============================================
        logger.info(f"\n[Pass 1] 生成因果图谱拓扑结构")
        topology = await self._pass1_generate_topology(query, context)
        
        logger.info(f"[Pass 1] 完成")
        logger.info(f"  - 节点数: {len(topology['nodes'])}")
        logger.info(f"  - 边数: {len(topology['edges'])}")
        
        # ============================================
        # Pass 2: 动态富化 + 数据溯源
        # ============================================
        logger.info(f"\n[Pass 2] 动态富化节点状态并追溯数据源")
        enriched_graph = await self._pass2_enrich_with_provenance(topology)
        
        # 统计溯源数据
        total_sources = sum(
            len(node.get('realtime_state', {}).get('sources', []))
            for node in enriched_graph['nodes']
        )
        logger.info(f"[Pass 2] 完成")
        logger.info(f"  - 获取数据源: {total_sources} 条")
        
        logger.info(f"\n{'='*80}")
        logger.info(f"[双阶段分析] 完成")
        logger.info(f"{'='*80}\n")
        
        return enriched_graph
    
    async def _pass1_generate_topology(
        self, 
        query: str, 
        context: Optional[str]
    ) -> Dict[str, Any]:
        """
        Pass 1: 生成因果图谱拓扑结构
        
        关键：每个节点必须包含 search_query 字段
        """
        system_prompt = """你是一个专业的因果分析专家。请分析问题的因果关系，构建因果图谱。

【输出格式】
必须严格输出以下 JSON 格式：
{
    "nodes": [
        {
            "id": "n1",
            "label": "节点标签（简短中文）",
            "type": "cause|effect|intermediate",
            "description": "节点详细描述",
            "search_query": "用于搜索该节点最新状态的关键词"
        }
    ],
    "edges": [
        {
            "source": "n1",
            "target": "n2",
            "label": "因果关系类型",
            "strength": 0.85
        }
    ],
    "explanation": "整体因果关系的文字解释"
}

【关键要求 - 节点标签规则】
⚠️ 重要：label 字段必须使用中文，这是显示给用户看的！
- label: "铜价" ✅ 正确
- label: "Copper Price" ❌ 错误
- label: "经济增长" ✅ 正确  
- label: "Economic Growth" ❌ 错误

【关键要求 - Search Query 生成规则】
1. search_query 必须是极简的 SEO 关键词，不要用完整句子
2. 如果要找数值，直接写 [指标名称] current rate value 2026
3. 避免冗余词汇，优先使用英文关键词（搜索引擎友好）
4. 包含时效性词汇：latest, current, 2026, today

【正确示例】
节点 label: "美元指数" （中文）
search_query: "US Dollar Index DXY current value 2026" （英文）

节点 label: "美联储利率" （中文）
search_query: "Federal Reserve interest rate current 2026" （英文）

节点 label: "黄金价格" （中文）
search_query: "gold price per ounce current 2026" （英文）

【错误示例】
❌ label: "Copper Price" （应该用中文"铜价"）
❌ search_query: "请帮我查询美元指数的最新走势和分析报告"（太冗长）
❌ search_query: "美元指数"（缺少时效性和数值关键词）
"""

        user_prompt = f"""请分析以下问题的因果关系：

问题：{query}
"""
        
        if context:
            user_prompt += f"\n背景信息：{context}\n"
        
        user_prompt += """
请生成因果图谱，确保每个节点都包含 search_query 字段。
"""

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
        
        # 验证每个节点是否包含 search_query
        for node in result["nodes"]:
            if "search_query" not in node:
                logger.warning(f"[Pass 1] 节点 {node.get('id')} 缺少 search_query，自动生成")
                node["search_query"] = f"{node.get('label', '')} latest news"
        
        return result
    
    async def _pass2_enrich_with_provenance(
        self, 
        topology: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Pass 2: 动态富化节点状态并追溯数据源
        
        工作流程：
        1. 提取所有节点的 search_query
        2. 并发调用搜索引擎（真实 API 或 Mock）
        3. 解析搜索结果为 realtime_state
        4. 注入 sources 数组（包含 title, url, domain）
        """
        nodes = topology["nodes"]
        
        # 并发处理所有节点
        enriched_nodes = await asyncio.gather(
            *[self._enrich_single_node(node) for node in nodes],
            return_exceptions=True
        )
        
        # 过滤异常结果
        valid_nodes = []
        for i, result in enumerate(enriched_nodes):
            if isinstance(result, Exception):
                logger.error(f"[Pass 2] 节点 {i} 富化失败: {str(result)}")
                valid_nodes.append(nodes[i])  # 使用原始节点
            else:
                valid_nodes.append(result)
        
        # 返回富化后的图谱
        return {
            "nodes": valid_nodes,
            "edges": topology["edges"],
            "explanation": topology["explanation"]
        }
    
    async def _enrich_single_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        富化单个节点的实时状态（集成两阶段共识验证）
        
        路由优先级：
        1. Yahoo Finance 直连（资产价格类节点）
        2. 两阶段共识验证（白名单 + 三方交叉验证）
        
        Args:
            node: 包含 search_query 和 type 的节点
            
        Returns:
            富化后的节点（包含 realtime_state）
        """
        node_id = node.get("id", "unknown")
        node_label = node.get("label", "unknown")
        node_type = node.get("type", "intermediate")
        search_query = node.get("search_query", "")
        
        if not search_query:
            logger.warning(f"[Pass 2] 节点 {node_id} 缺少 search_query，跳过富化")
            return node
        
        logger.info(f"[Pass 2] 富化节点: {node_label} (类型: {node_type})")
        
        try:
            # ============================================================
            # 路由决策 1: Yahoo Finance 直连旁路（最高优先级）
            # ============================================================
            yahoo_result = await self.yahoo_finance.fetch_by_node_label(node_label)
            
            if yahoo_result:
                logger.info(f"[Pass 2] ✓ Yahoo Finance 直连成功: {node_label}")
                
                # 构建 realtime_state
                realtime_state = {
                    "latest_value": yahoo_result["latest_value"],
                    "trend": yahoo_result.get("trend", "stable"),
                    "change_percent": yahoo_result.get("change_percent", "N/A"),
                    "sources": yahoo_result["sources"],
                    "updated_at": yahoo_result["updated_at"],
                    "strategy_used": "yahoo_finance_direct",
                    "confidence": "api_direct",
                    "metadata": yahoo_result.get("metadata", {})
                }
                
                node["realtime_state"] = realtime_state
                
                logger.info(
                    f"[Pass 2] 节点 {node_label} 富化完成: "
                    f"value={realtime_state['latest_value']}, "
                    f"trend={realtime_state['trend']}, "
                    f"strategy=yahoo_finance_direct"
                )
                
                return node
            
            # ============================================================
            # 路由决策 2: 两阶段共识验证（白名单 + 三方交叉验证）
            # ============================================================
            logger.info(f"[Pass 2] Yahoo Finance 未匹配，启动两阶段共识验证")
            
            # 调用 NodeSensingService 的两阶段验证
            from app.services.node_sensing_service import NodeSensingService
            sensing_service = NodeSensingService()
            
            # 构建临时节点对象（符合 NodeSensingService 的输入格式）
            temp_node = {
                "id": node_id,
                "label": node_label,
                "sensing_config": {
                    "auto_queries": [search_query]
                }
            }
            
            # 执行两阶段验证
            enriched_temp_node = await sensing_service.enrich_node_state(temp_node)
            
            # 提取结果
            current_state = enriched_temp_node.get("current_state", {})
            
            # 构建 realtime_state
            realtime_state = {
                "latest_value": current_state.get("value", "unknown"),
                "trend": current_state.get("trend", "stable"),
                "narrative_context": current_state.get("narrative_context", ""),
                "sources": current_state.get("sources", []),
                "updated_at": enriched_temp_node.get("last_updated"),
                "strategy_used": "two_stage_consensus",
                "confidence": current_state.get("confidence", "unknown")
            }
            
            # 注入到节点
            node["realtime_state"] = realtime_state
            
            logger.info(
                f"[Pass 2] 节点 {node_label} 富化完成: "
                f"value={realtime_state['latest_value']}, "
                f"confidence={realtime_state['confidence']}, "
                f"sources={len(realtime_state['sources'])}"
            )
            
            return node
            
        except Exception as e:
            logger.error(f"[Pass 2] 节点 {node_id} 富化失败: {str(e)}")
            # 返回带有 unknown 状态的节点
            node["realtime_state"] = {
                "latest_value": "unknown",
                "trend": "stable",
                "narrative_context": "数据获取失败",
                "sources": [],
                "updated_at": None,
                "strategy_used": "error",
                "confidence": "unknown"
            }
            return node
    
    async def _search(self, query: str) -> List[Dict[str, Any]]:
        """
        调用搜索引擎（真实 API 或 Mock）
        
        Returns:
            搜索结果列表，每个结果包含：
            - title: 标题
            - url: 链接
            - snippet: 摘要
        """
        if self.use_mock:
            return await self._mock_search_api(query)
        
        # 真实搜索引擎调用
        if self.tavily_api_key:
            return await self._search_tavily(query)
        elif self.serper_api_key:
            return await self._search_serper(query)
        
        return []
    
    async def _mock_search_api(self, query: str) -> List[Dict[str, Any]]:
        """
        Mock 搜索引擎 API（模拟网络延迟）
        
        用于开发/测试环境，模拟真实搜索结果
        """
        logger.info(f"[Mock Search] 模拟搜索: {query}")
        
        # 模拟网络延迟 (500ms - 1500ms)
        import random
        delay = random.uniform(0.5, 1.5)
        await asyncio.sleep(delay)
        
        # 根据查询关键词生成模拟结果
        mock_results = []
        
        if "美元" in query or "dollar" in query.lower():
            mock_results = [
                {
                    "title": "美元指数升至103.5，创两个月新高",
                    "url": "https://www.reuters.com/markets/currencies/dollar-index-2024",
                    "snippet": "美元指数周三升至103.5，受美联储鹰派立场支撑..."
                },
                {
                    "title": "US Dollar Index Rises on Fed Hawkish Stance",
                    "url": "https://www.bloomberg.com/news/dollar-strength-2024",
                    "snippet": "The US Dollar Index (DXY) climbed to 103.5..."
                }
            ]
        elif "利率" in query or "interest rate" in query.lower():
            mock_results = [
                {
                    "title": "美联储维持利率在5.25%-5.50%不变",
                    "url": "https://www.federalreserve.gov/newsevents/2024",
                    "snippet": "美联储宣布维持联邦基金利率目标区间在5.25%-5.50%..."
                },
                {
                    "title": "Fed Holds Rates Steady at 5.25%-5.50%",
                    "url": "https://www.cnbc.com/fed-decision-2024",
                    "snippet": "The Federal Reserve kept interest rates unchanged..."
                }
            ]
        elif "黄金" in query or "gold" in query.lower():
            mock_results = [
                {
                    "title": "黄金价格突破2025美元/盎司",
                    "url": "https://www.kitco.com/gold-price-2024",
                    "snippet": "国际黄金价格周三突破2025美元/盎司，创历史新高..."
                },
                {
                    "title": "Gold Prices Hit Record High at $2025/oz",
                    "url": "https://www.marketwatch.com/gold-2024",
                    "snippet": "Gold prices surged to a record $2025 per ounce..."
                }
            ]
        else:
            # 通用模拟结果
            mock_results = [
                {
                    "title": f"关于 {query} 的最新分析报告",
                    "url": f"https://www.example.com/analysis/{query.replace(' ', '-')}",
                    "snippet": f"最新数据显示，{query} 呈现稳定态势..."
                },
                {
                    "title": f"Latest Update on {query}",
                    "url": f"https://www.news.com/latest/{query.replace(' ', '-')}",
                    "snippet": f"Recent developments in {query} show..."
                }
            ]
        
        logger.info(f"[Mock Search] 返回 {len(mock_results)} 条模拟结果")
        return mock_results
    
    async def _search_tavily(self, query: str) -> List[Dict[str, Any]]:
        """调用 Tavily API"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "api_key": self.tavily_api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": 3
            }
            
            async with session.post(
                "https://api.tavily.com/search", 
                json=payload
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"Tavily API 返回错误: {resp.status}")
                
                data = await resp.json()
                results = data.get("results", [])
                
                return [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "snippet": r.get("content", "")
                    }
                    for r in results
                ]
    
    async def _search_serper(self, query: str) -> List[Dict[str, Any]]:
        """调用 Serper API"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }
            payload = {"q": query, "num": 3}
            
            async with session.post(
                "https://google.serper.dev/search",
                json=payload,
                headers=headers
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"Serper API 返回错误: {resp.status}")
                
                data = await resp.json()
                results = data.get("organic", [])
                
                return [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("link", ""),
                        "snippet": r.get("snippet", "")
                    }
                    for r in results
                ]
    
    async def _parse_search_results_with_llm(
        self,
        node_label: str,
        search_results: List[Dict[str, Any]],
        attempt_number: int = 1,
        authority_check: bool = False
    ) -> str:
        """
        使用 LLM 解析搜索结果，提取最新数值或状态
        
        Args:
            node_label: 节点标签
            search_results: 搜索结果列表
            attempt_number: 尝试次数（1=白名单，2=全网）
            authority_check: 是否启用权威性判断
        
        Returns:
            提取的最新值（字符串）
        """
        # 构建搜索结果上下文
        context = "\n\n".join([
            f"[来源 {i+1}]\n标题: {r['title']}\n链接: {r['url']}\n摘要: {r.get('snippet', '')}"
            for i, r in enumerate(search_results[:5])
        ])
        
        # 基础 Prompt
        base_system_prompt = """你是一个数据提取专家。请从搜索结果中提取节点的最新状态。

【输出格式】
必须严格输出以下 JSON 格式：
{
    "latest_value": "提取的最新数值或状态描述"
}

【提取规则】
1. 如果搜索结果中有明确数值，提取数值（如 "103.5", "5.25%-5.50%", "2025美元/盎司"）
2. 如果没有明确数值，用简短描述（如 "持续上涨", "保持稳定", "风险上升"）
3. 如果完全无法确定，设为 "unknown"
4. 不要编造数据，严格基于搜索结果"""
        
        # Attempt 2 额外护栏：权威性判断
        authority_guard = ""
        if authority_check:
            authority_guard = """

【重要：权威性判断】
⚠️ 这批数据来自无限制全网搜索，请严格判断来源权威性：
- 如果来源是博客、内容农场、自媒体、论坛帖子，必须返回 "unknown"
- 只接受：主流财经媒体、官方机构、知名金融网站
- 判断标准：域名是否为知名机构（如 .gov, .org, 主流媒体）
- 如果无法确认来源权威性，宁可返回 "unknown"
"""
        
        system_prompt = base_system_prompt + authority_guard
        
        user_prompt = f"""【节点名称】
{node_label}

【搜索结果】
{context}

【当前尝试】
Attempt {attempt_number} {"(白名单搜索)" if attempt_number == 1 else "(全网搜索 - 需判断权威性)"}

请提取该节点的最新状态。"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            extracted_value = result.get("latest_value", "unknown")
            
            logger.info(
                f"[LLM 解析] Attempt {attempt_number} 完成: "
                f"{node_label} = {extracted_value}"
            )
            
            return extracted_value
            
        except Exception as e:
            logger.error(f"[LLM 解析] 失败: {str(e)}")
            return "unknown"


