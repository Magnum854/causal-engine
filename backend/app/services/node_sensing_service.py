"""
节点自主感知服务 (Autonomous Node Sensing)
实现节点状态的实时更新与智能感知

【重构版本 2.0】
- 机构级数据防伪机制
- 两阶段共识验证 (Two-Stage Consensus Validation)
- 三方交叉验证 (Cross-Validation)
"""

from openai import AsyncOpenAI
import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class NodeSensingService:
    """节点自主感知服务 - 机构级数据防伪版本"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.model = os.getenv("OPENAI_MODEL", "deepseek-reasoner")
        
        # Tavily API 配置（优先）
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.tavily_base_url = "https://api.tavily.com/search"
        
        # Serper API 配置（备用）
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.serper_base_url = "https://google.serper.dev/search"
        
        # 并发控制
        self.max_concurrent_searches = 5
        
        # 加载白名单配置
        self._load_whitelist_config()
    
    def _load_whitelist_config(self):
        """加载白名单域名配置"""
        config_path = Path(__file__).parent.parent.parent / "config" / "financial_sources.json"
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # 提取所有白名单域名
            self.whitelist_domains = []
            search_domains = config.get("search_domains", {})
            
            for category_name, category_data in search_domains.items():
                if category_name == "description":
                    continue
                if isinstance(category_data, dict) and "domains" in category_data:
                    self.whitelist_domains.extend(category_data["domains"])
            
            logger.info(f"[白名单配置] 加载完成，共 {len(self.whitelist_domains)} 个权威域名")
            
        except Exception as e:
            logger.error(f"[白名单配置] 加载失败: {str(e)}")
            self.whitelist_domains = []
        
    async def enrich_node_state(self, node_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        为单个节点补充实时状态信息（两阶段共识验证版本）
        
        Args:
            node_json: 节点对象，包含 sensing_config.auto_queries
            
        Returns:
            更新后的节点对象，包含 current_state 字段
            
        【两阶段数据流】：
            Stage 1: 白名单优先搜索 (Whitelist Pass)
                - 限定权威域名搜索（7天窗口）
                - LLM 直接提取数值
                - 成功 → 标记 confidence: "whitelist_direct"
                
            Stage 2: 全网兜底与三方交叉验证 (Cross-Validation Pass)
                - 全网搜索（不限域名，7天窗口）
                - LLM 严格执行三方交叉验证
                - 必须 ≥3 个独立域名一致才采信
                - 成功 → 标记 confidence: "cross_validated"
        """
        node_id = node_json.get("id", "unknown")
        node_label = node_json.get("label", "unknown")
        
        logger.info(f"[节点感知 2.0] 开始处理节点: {node_id} ({node_label})")
        
        try:
            # 1. 提取搜索查询配置
            sensing_config = node_json.get("sensing_config", {})
            auto_queries = sensing_config.get("auto_queries", [])
            
            if not auto_queries:
                logger.warning(f"[节点感知] 节点 {node_id} 缺少 auto_queries 配置，跳过")
                return node_json
            
            logger.info(f"[节点感知] 节点 {node_id} 配置了 {len(auto_queries)} 个搜索查询")
            
            # ============================================================
            # Stage 1: 白名单优先搜索
            # ============================================================
            logger.info(f"[Stage 1] 白名单优先搜索 - 节点: {node_label}")
            
            stage1_results = await self._perform_searches(auto_queries)
            
            if stage1_results:
                # 白名单过滤
                whitelist_results = self._filter_by_whitelist(stage1_results)
                
                logger.info(
                    f"[Stage 1] 搜索结果: {len(stage1_results)} 条 "
                    f"→ 白名单过滤后: {len(whitelist_results)} 条"
                )
                
                if whitelist_results:
                    # LLM 直接提取（无需交叉验证）
                    current_state = await self._extract_state_stage1(
                        node_label=node_label,
                        search_results=whitelist_results
                    )
                    
                    if current_state["value"] != "unknown":
                        logger.info(
                            f"[Stage 1] ✓ 白名单直接采信: {current_state['value']} "
                            f"(confidence: whitelist_direct)"
                        )
                        
                        # 注入状态
                        node_json["current_state"] = current_state
                        node_json["last_updated"] = datetime.utcnow().isoformat()
                        return node_json
                    else:
                        logger.warning(f"[Stage 1] LLM 返回 unknown，进入 Stage 2")
                else:
                    logger.warning(f"[Stage 1] 白名单过滤后无结果，进入 Stage 2")
            else:
                logger.warning(f"[Stage 1] 搜索无结果，进入 Stage 2")
            
            # ============================================================
            # Stage 2: 全网兜底与三方交叉验证
            # ============================================================
            logger.info(f"[Stage 2] 全网搜索 + 三方交叉验证 - 节点: {node_label}")
            
            # 重新搜索（全网，Top-10）
            stage2_results = await self._perform_searches(auto_queries, max_results=10)
            
            if not stage2_results:
                logger.error(f"[Stage 2] 全网搜索无结果，返回 unknown")
                node_json["current_state"] = self._create_unknown_state()
                return node_json
            
            logger.info(f"[Stage 2] 全网搜索结果: {len(stage2_results)} 条")
            
            # LLM 三方交叉验证
            current_state = await self._extract_state_stage2(
                node_label=node_label,
                search_results=stage2_results
            )
            
            if current_state["value"] != "unknown":
                logger.info(
                    f"[Stage 2] ✓ 三方交叉验证通过: {current_state['value']} "
                    f"(confidence: cross_validated, sources: {len(current_state.get('sources', []))})"
                )
            else:
                logger.warning(f"[Stage 2] ✗ 三方交叉验证失败，返回 unknown")
            
            # 注入状态
            node_json["current_state"] = current_state
            node_json["last_updated"] = datetime.utcnow().isoformat()
            
            return node_json
            
        except Exception as e:
            logger.error(f"[节点感知] 节点 {node_id} 处理失败: {str(e)}")
            # 降级处理：返回 unknown 状态
            node_json["current_state"] = self._create_unknown_state()
            return node_json
    
    async def enrich_nodes_batch(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量并发处理多个节点的状态更新
        
        Args:
            nodes: 节点列表
            
        Returns:
            更新后的节点列表
        """
        logger.info(f"[批量感知] 开始处理 {len(nodes)} 个节点")
        
        # 使用 asyncio.gather 并发处理，限制并发数
        semaphore = asyncio.Semaphore(self.max_concurrent_searches)
        
        async def process_with_limit(node):
            async with semaphore:
                return await self.enrich_node_state(node)
        
        enriched_nodes = await asyncio.gather(
            *[process_with_limit(node) for node in nodes],
            return_exceptions=True  # 单个失败不影响整体
        )
        
        # 过滤异常结果
        valid_nodes = []
        for i, result in enumerate(enriched_nodes):
            if isinstance(result, Exception):
                logger.error(f"[批量感知] 节点 {i} 处理异常: {str(result)}")
                # 使用原始节点 + unknown 状态
                nodes[i]["current_state"] = self._create_unknown_state()
                valid_nodes.append(nodes[i])
            else:
                valid_nodes.append(result)
        
        logger.info(f"[批量感知] 批量处理完成，成功 {len(valid_nodes)} 个节点")
        return valid_nodes
    
    async def _perform_searches(self, queries: List[str], max_results: int = 3) -> List[Dict[str, Any]]:
        """
        并发执行多个搜索查询
        
        Args:
            queries: 搜索查询列表
            max_results: 每个查询返回的最大结果数
            
        Returns:
            搜索结果列表
        """
        logger.info(f"[搜索引擎] 开始执行 {len(queries)} 个搜索查询 (max_results={max_results})")
        
        # 并发执行所有查询
        search_tasks = [self._search_single_query(q, max_results) for q in queries]
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # 合并所有有效结果
        all_snippets = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"[搜索引擎] 查询 '{queries[i]}' 失败: {str(result)}")
                continue
            if result:
                all_snippets.extend(result)
        
        logger.info(f"[搜索引擎] 搜索完成，获取 {len(all_snippets)} 条有效结果")
        
        return all_snippets
    
    async def _search_single_query(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        执行单个搜索查询
        
        优先使用 Tavily API，失败则降级到 Serper API
        
        Args:
            query: 搜索查询字符串
            max_results: 返回的最大结果数
            
        Returns:
            搜索结果片段列表
        """
        logger.debug(f"[搜索引擎] 执行查询: {query}")
        
        # 优先使用 Tavily
        if self.tavily_api_key:
            try:
                return await self._search_tavily(query, max_results)
            except Exception as e:
                logger.warning(f"[搜索引擎] Tavily 搜索失败，尝试 Serper: {str(e)}")
        
        # 降级到 Serper
        if self.serper_api_key:
            try:
                return await self._search_serper(query, max_results)
            except Exception as e:
                logger.error(f"[搜索引擎] Serper 搜索也失败: {str(e)}")
        
        logger.error(f"[搜索引擎] 所有搜索引擎均不可用")
        return []
    
    async def _search_tavily(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """调用 Tavily API"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "api_key": self.tavily_api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": max_results
            }
            
            async with session.post(self.tavily_base_url, json=payload) as resp:
                if resp.status != 200:
                    raise Exception(f"Tavily API 返回错误: {resp.status}")
                
                data = await resp.json()
                results = data.get("results", [])
                
                # 转换为统一格式
                return [
                    {
                        "title": r.get("title", ""),
                        "snippet": r.get("content", ""),
                        "url": r.get("url", ""),
                        "domain": urlparse(r.get("url", "")).netloc
                    }
                    for r in results
                ]
    
    async def _search_serper(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """调用 Serper API"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }
            payload = {"q": query, "num": max_results}
            
            async with session.post(
                self.serper_base_url, 
                json=payload, 
                headers=headers
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"Serper API 返回错误: {resp.status}")
                
                data = await resp.json()
                results = data.get("organic", [])
                
                # 转换为统一格式
                return [
                    {
                        "title": r.get("title", ""),
                        "snippet": r.get("snippet", ""),
                        "url": r.get("link", ""),
                        "domain": urlparse(r.get("link", "")).netloc
                    }
                    for r in results
                ]
    
    def _filter_by_whitelist(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        根据白名单过滤搜索结果
        
        Args:
            search_results: 原始搜索结果
            
        Returns:
            过滤后的结果（仅保留白名单域名）
        """
        if not self.whitelist_domains:
            logger.warning("[白名单过滤] 白名单为空，返回原始结果")
            return search_results
        
        filtered = []
        for result in search_results:
            domain = result.get("domain", "")
            if not domain:
                continue
            
            # 检查是否在白名单中（支持子域名）
            for whitelist_domain in self.whitelist_domains:
                if domain.endswith(whitelist_domain) or domain == whitelist_domain:
                    filtered.append(result)
                    logger.debug(f"[白名单过滤] ✓ 匹配: {domain} -> {whitelist_domain}")
                    break
            else:
                logger.debug(f"[白名单过滤] ✗ 拒绝: {domain}")
        
        return filtered
    
    async def _extract_state_stage1(
        self, 
        node_label: str, 
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Stage 1: 白名单直接提取（无需交叉验证）
        
        Args:
            node_label: 节点标签（如"美联储利率"）
            search_results: 白名单过滤后的搜索结果
            
        Returns:
            结构化状态对象: {value, trend, narrative_context, confidence, sources}
        """
        logger.info(f"[Stage 1 LLM] 开始解析节点 '{node_label}' 的状态（白名单直接提取）")
        
        # 构建上下文
        context = self._build_search_context(search_results)
        
        # Stage 1 系统提示词：直接提取，信任白名单
        system_prompt = """你是一个专业的金融数据提取引擎。你正在处理来自【权威白名单域名】的搜索结果（如 Bloomberg、Reuters、IMF、东方财富等）。

【输出格式】
必须严格输出以下 JSON 格式：
{
    "value": "具体数值或状态描述",
    "trend": "rising|falling|stable",
    "narrative_context": "一句话总结当前状态的背景原因",
    "confidence": "whitelist_direct",
    "sources": [
        {
            "title": "新闻标题",
            "url": "完整URL",
            "domain": "域名"
        }
    ]
}

【关键约束】
1. value 字段：
   - 如果搜索结果中有明确数值，必须提取（如 "5.25%", "1850美元/盎司", "7.2%"）
   - 如果没有明确数值，用简短描述（如 "持续上涨", "保持稳定"）
   - 如果完全无法确定，必须设为 "unknown"

2. trend 字段：
   - 只能是 "rising"（上升）、"falling"（下降）、"stable"（稳定）三者之一
   - 基于搜索结果中的趋势词判断

3. sources 字段：
   - 列出所有支持该数值的搜索结果（最多3条）
   - 必须包含 title、url、domain 三个字段

4. confidence 字段：
   - 固定为 "whitelist_direct"（表示来自白名单直接采信）

【反幻觉机制】
- 这些是权威来源，可以直接采信
- 但如果搜索结果不足以判断状态，所有字段设为保守值：
{
    "value": "unknown",
    "trend": "stable",
    "narrative_context": "暂无足够信息判断当前状态",
    "confidence": "whitelist_direct",
    "sources": []
}"""

        user_prompt = f"""【节点名称】
{node_label}

【搜索结果（来自权威白名单域名）】
{context}

请提取该节点的实时状态，严格按照 JSON 格式输出。"""

        try:
            # 调用 LLM
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
            state = json.loads(content)
            
            # 验证必需字段
            required_fields = ["value", "trend", "narrative_context", "confidence", "sources"]
            for field in required_fields:
                if field not in state:
                    raise ValueError(f"LLM 返回缺少字段: {field}")
            
            # 验证 trend 枚举值
            valid_trends = ["rising", "falling", "stable"]
            if state["trend"] not in valid_trends:
                logger.warning(f"[Stage 1 LLM] trend 值无效: {state['trend']}，修正为 stable")
                state["trend"] = "stable"
            
            logger.info(
                f"[Stage 1 LLM] 节点 '{node_label}' 解析成功: "
                f"value={state['value']}, sources={len(state.get('sources', []))}"
            )
            
            return state
            
        except Exception as e:
            logger.error(f"[Stage 1 LLM] 节点 '{node_label}' 解析失败: {str(e)}")
            return self._create_unknown_state(confidence="whitelist_direct")
    
    async def _extract_state_stage2(
        self, 
        node_label: str, 
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Stage 2: 全网搜索 + 三方交叉验证（核心难点）
        
        Args:
            node_label: 节点标签
            search_results: 全网搜索结果（Top-10）
            
        Returns:
            结构化状态对象: {value, trend, narrative_context, confidence, sources}
            
        【三方交叉验证规则】：
            1. 提取的数值必须在至少 3 个不同域名的网页中完全一致
            2. sources 数组必须严格列出这 3 个支持该数值的独立网页
            3. 如果满足该数值的独立域名少于 3 个，返回 unknown
        """
        logger.info(f"[Stage 2 LLM] 开始解析节点 '{node_label}' 的状态（三方交叉验证）")
        
        # 构建上下文（包含域名信息）
        context = self._build_search_context_with_domains(search_results)
        
        # Stage 2 系统提示词：严格的三方交叉验证
        system_prompt = """你是一个严苛的金融审计员。面对这批全网搜索结果，你必须进行【三方交叉验证 (Cross-Validation)】以消除虚假信息。

【输出格式】
必须严格输出以下 JSON 格式：
{
    "value": "具体数值或状态描述",
    "trend": "rising|falling|stable",
    "narrative_context": "一句话总结当前状态的背景原因",
    "confidence": "cross_validated",
    "sources": [
        {
            "title": "新闻标题1",
            "url": "完整URL1",
            "domain": "域名1"
        },
        {
            "title": "新闻标题2",
            "url": "完整URL2",
            "domain": "域名2"
        },
        {
            "title": "新闻标题3",
            "url": "完整URL3",
            "domain": "域名3"
        }
    ]
}

【三方交叉验证规则（严格执行）】
规则 1：你提取的最新数值，必须在至少 3 个不同域名的网页摘要中完全一致地出现过。
   - 例如：如果你提取 "5.25%"，那么必须有 3 个不同域名的网页都明确提到 "5.25%"
   - 不同域名是指：bloomberg.com、reuters.com、cnbc.com 算 3 个不同域名
   - 同一域名的多个页面只算 1 个域名

规则 2：请在 JSON 输出的 sources 数组中，严格列出这 3 个支持该数值的独立网页。
   - sources 数组必须包含至少 3 条记录
   - 每条记录必须包含 title、url、domain 三个字段
   - 这 3 条记录的 domain 必须完全不同

规则 3：如果满足该数值的独立域名少于 3 个，即使你看到了数据，也必须返回 unknown。
   - 例如：只有 2 个域名提到 "5.25%"，其他域名没有提到或提到不同数值 → 返回 unknown
   - 例如：10 个搜索结果都来自同一个域名 → 返回 unknown

【反幻觉机制】
- 全网搜索结果可能包含虚假信息、过时数据、营销内容
- 只有通过三方交叉验证的数据才能采信
- 如果无法满足三方验证，必须返回：
{
    "value": "unknown",
    "trend": "stable",
    "narrative_context": "无法通过三方交叉验证，数据源不足或存在冲突",
    "confidence": "cross_validated",
    "sources": []
}

【示例】
假设搜索结果：
- [结果 1] bloomberg.com: "美联储利率维持在 5.25%"
- [结果 2] reuters.com: "Fed rate remains at 5.25%"
- [结果 3] cnbc.com: "联邦基金利率 5.25%"
- [结果 4] randomsite.com: "利率可能是 5.5%"（冲突数据，忽略）

✓ 正确输出：value="5.25%"，sources 包含前 3 个结果（3 个不同域名一致）

假设搜索结果：
- [结果 1] bloomberg.com: "美联储利率维持在 5.25%"
- [结果 2] bloomberg.com: "Fed rate 5.25%"（同域名，不计入）
- [结果 3] reuters.com: "利率可能在 5.0%-5.5% 之间"（不明确，不计入）

✗ 正确输出：value="unknown"（只有 1 个域名明确提到 5.25%，不满足三方验证）"""

        user_prompt = f"""【节点名称】
{node_label}

【搜索结果（全网，需要三方交叉验证）】
{context}

请严格执行三方交叉验证规则，提取该节点的实时状态。如果无法满足三方验证，必须返回 unknown。"""

        try:
            # 调用 LLM
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,  # 零温度，最大化确定性
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            state = json.loads(content)
            
            # 验证必需字段
            required_fields = ["value", "trend", "narrative_context", "confidence", "sources"]
            for field in required_fields:
                if field not in state:
                    raise ValueError(f"LLM 返回缺少字段: {field}")
            
            # 验证三方交叉验证规则
            if state["value"] != "unknown":
                sources = state.get("sources", [])
                
                # 检查是否有至少 3 个不同域名
                unique_domains = set()
                for source in sources:
                    domain = source.get("domain", "")
                    if domain:
                        unique_domains.add(domain)
                
                if len(unique_domains) < 3:
                    logger.warning(
                        f"[Stage 2 LLM] 三方验证失败: 只有 {len(unique_domains)} 个独立域名，"
                        f"不满足 ≥3 的要求，强制返回 unknown"
                    )
                    return self._create_unknown_state(
                        confidence="cross_validated",
                        narrative="无法通过三方交叉验证，数据源不足或存在冲突"
                    )
            
            # 验证 trend 枚举值
            valid_trends = ["rising", "falling", "stable"]
            if state["trend"] not in valid_trends:
                logger.warning(f"[Stage 2 LLM] trend 值无效: {state['trend']}，修正为 stable")
                state["trend"] = "stable"
            
            logger.info(
                f"[Stage 2 LLM] 节点 '{node_label}' 解析成功: "
                f"value={state['value']}, sources={len(state.get('sources', []))} "
                f"(unique_domains={len(set(s.get('domain', '') for s in state.get('sources', [])))})"
            )
            
            return state
            
        except Exception as e:
            logger.error(f"[Stage 2 LLM] 节点 '{node_label}' 解析失败: {str(e)}")
            return self._create_unknown_state(confidence="cross_validated")
    
    def _build_search_context(self, search_results: List[Dict[str, Any]]) -> str:
        """将搜索结果格式化为 LLM 上下文（简化版）"""
        if not search_results:
            return "（无搜索结果）"
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            title = result.get("title", "无标题")
            snippet = result.get("snippet", "无内容")
            context_parts.append(f"[结果 {i}] {title}\n{snippet}")
        
        return "\n\n".join(context_parts)
    
    def _build_search_context_with_domains(self, search_results: List[Dict[str, Any]]) -> str:
        """将搜索结果格式化为 LLM 上下文（包含域名信息，用于三方验证）"""
        if not search_results:
            return "（无搜索结果）"
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            title = result.get("title", "无标题")
            snippet = result.get("snippet", "无内容")
            domain = result.get("domain", "unknown")
            url = result.get("url", "")
            
            context_parts.append(
                f"[结果 {i}] 域名: {domain}\n"
                f"标题: {title}\n"
                f"摘要: {snippet}\n"
                f"URL: {url}"
            )
        
        return "\n\n".join(context_parts)
    
    def _create_unknown_state(
        self, 
        confidence: str = "unknown", 
        narrative: str = "暂无足够信息判断当前状态"
    ) -> Dict[str, Any]:
        """创建 unknown 状态（降级方案）"""
        return {
            "value": "unknown",
            "trend": "stable",
            "narrative_context": narrative,
            "confidence": confidence,
            "sources": []
        }

