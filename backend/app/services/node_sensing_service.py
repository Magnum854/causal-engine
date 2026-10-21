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

# 导入置信度计算器
from app.utils.confidence_calculator import calculate_node_confidence

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
            api_key=os.getenv("OPENAI_API_KEY") or "missing-key",
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            timeout=60.0  # 60秒超时
        )
        self.model = os.getenv("OPENAI_MODEL", "deepseek-reasoner")
        
        # Tavily API 配置（优先）
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.tavily_base_url = "https://api.tavily.com/search"
        
        # Serper API 配置（备用）
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.serper_base_url = "https://google.serper.dev/search"
        
        # 并发控制（优化：提高并发数）
        self.max_concurrent_searches = 10
        self.search_timeout_seconds = 15
        self.search_retry_attempts = 3
        self._search_cache: Dict[str, tuple] = {}
        self._search_cache_ttl_seconds = 15 * 60
        
        # 加载白名单配置
        self._load_whitelist_config()
    
    def _is_qualitative_node(self, node_type: str) -> bool:
        """
        判断节点是否为定性类型
        
        Args:
            node_type: 节点类型
            
        Returns:
            True 表示定性节点，False 表示定量节点
        """
        if not node_type:
            return False
        
        # 检查是否在定性类型集合中
        if node_type in self.qualitative_types:
            return True
        
        # 检查是否在定量类型集合中
        if node_type in self.quantitative_types:
            return False
        
        # 默认：未知类型视为定量（保守策略）
        logger.warning(f"[节点分类] 未知节点类型: {node_type}，默认视为定量型")
        return False
    
    def _get_intensity_scale(self, node_type: str) -> str:
        """
        获取定性节点的强度等级类型
        
        Args:
            node_type: 节点类型
            
        Returns:
            强度等级类型: risk_based, sentiment_based, trend_based, expectation_based
        """
        routing_rules = self.config.get("routing_rules", {})
        rule = routing_rules.get(node_type, {})
        
        # 从路由规则中获取强度等级类型
        intensity_scale = rule.get("intensity_scale", "risk_based")
        
        return intensity_scale
    
    def _load_whitelist_config(self):
        """加载白名单域名配置和节点类型分类"""
        config_path = Path(__file__).parent.parent.parent / "config" / "financial_sources.json"
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            
            # 提取所有白名单域名
            self.whitelist_domains = []
            search_domains = self.config.get("search_domains", {})
            
            for category_name, category_data in search_domains.items():
                if category_name == "description":
                    continue
                if isinstance(category_data, dict) and "domains" in category_data:
                    self.whitelist_domains.extend(category_data["domains"])
            
            # 加载节点类型分类
            node_categories = self.config.get("node_type_categories", {})
            self.quantitative_types = set(node_categories.get("quantitative", {}).get("types", []))
            self.qualitative_types = set(node_categories.get("qualitative", {}).get("types", []))
            self.intensity_levels = node_categories.get("qualitative", {}).get("intensity_levels", {})
            
            logger.info(f"[白名单配置] 加载完成，共 {len(self.whitelist_domains)} 个权威域名")
            logger.info(f"[节点分类] 定量型: {len(self.quantitative_types)} 种，定性型: {len(self.qualitative_types)} 种")
            
        except Exception as e:
            logger.error(f"[白名单配置] 加载失败: {str(e)}")
            self.whitelist_domains = []
            self.quantitative_types = set()
            self.qualitative_types = set()
            self.intensity_levels = {}
        
    async def enrich_node_state(self, node_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        为单个节点补充实时状态信息（优化版：保留两阶段但加速）
        
        Args:
            node_json: 节点对象，包含 sensing_config.auto_queries
            
        Returns:
            更新后的节点对象，包含 current_state 字段
            
        【优化策略】：
            - Stage 1: 白名单搜索（快速路径）
            - Stage 2: 全网搜索但简化验证（保证数据可用性）
            - 优化点：减少搜索结果数、简化 LLM Prompt、提高并发
        """
        node_id = node_json.get("id", "unknown")
        node_label = node_json.get("label", "unknown")
        node_type = node_json.get("type", "")
        
        # 判断节点类型（定量 vs 定性）
        is_qualitative = self._is_qualitative_node(node_type)
        node_category = "定性" if is_qualitative else "定量"
        
        logger.info(f"[节点感知] 处理: {node_label} ({node_category})")
        
        try:
            # 1. 提取搜索查询配置
            sensing_config = node_json.get("sensing_config", {})
            auto_queries = sensing_config.get("auto_queries", [])
            
            if not auto_queries:
                logger.warning(f"[节点感知] 节点 {node_id} 缺少查询配置")
                return node_json
            
            # ============================================================
            # Stage 1: 白名单优先搜索
            # ============================================================
            stage1_results = await self._perform_searches(auto_queries, max_results=3)
            
            if stage1_results:
                whitelist_results = self._filter_by_whitelist(stage1_results)
                
                if whitelist_results:
                    # 根据节点类型选择提取方法
                    if is_qualitative:
                        current_state = await self._extract_qualitative_state_stage1(
                            node_label=node_label,
                            node_type=node_type,
                            search_results=whitelist_results
                        )
                    else:
                        current_state = await self._extract_quantitative_state_stage1(
                            node_label=node_label,
                            search_results=whitelist_results
                        )
                    
                    if current_state["value"] != "unknown":
                        # 计算置信度分数
                        llm_confidence = node_json.get("confidence", 0.8)
                        sources = current_state.get("sources", [])
                        confidence_result = calculate_node_confidence(sources, llm_confidence)
                        
                        current_state["confidence_score"] = confidence_result["final_score"]
                        current_state["confidence_dimensions"] = confidence_result["dimensions"]
                        current_state["confidence_rating"] = confidence_result["rating"]
                        
                        node_json["current_state"] = current_state
                        node_json["last_updated"] = datetime.utcnow().isoformat()
                        return node_json
            
            # ============================================================
            # Stage 2: 全网搜索（简化版，保证数据可用性）
            # ============================================================
            logger.info(f"[Stage 2] 全网搜索: {node_label}")
            
            # 全网搜索（减少结果数：10 → 5）
            stage2_results = await self._perform_searches(auto_queries, max_results=5)
            
            if not stage2_results:
                logger.warning(f"[Stage 2] 无搜索结果")
                node_json["current_state"] = self._create_unknown_state()
                return node_json
            
            # 简化提取（不要求严格的三方验证）
            if is_qualitative:
                current_state = await self._extract_qualitative_state_simple(
                    node_label=node_label,
                    node_type=node_type,
                    search_results=stage2_results
                )
            else:
                current_state = await self._extract_quantitative_state_simple(
                    node_label=node_label,
                    search_results=stage2_results
                )
            
            # 计算置信度分数
            llm_confidence = node_json.get("confidence", 0.6)
            sources = current_state.get("sources", [])
            confidence_result = calculate_node_confidence(sources, llm_confidence)
            
            current_state["confidence_score"] = confidence_result["final_score"]
            current_state["confidence_dimensions"] = confidence_result["dimensions"]
            current_state["confidence_rating"] = confidence_result["rating"]
            
            node_json["current_state"] = current_state
            node_json["last_updated"] = datetime.utcnow().isoformat()
            
            return node_json
            
        except Exception as e:
            logger.error(f"[节点感知] 节点 {node_id} 处理失败: {str(e)}")
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
        
        # 最终降级：返回空结果（避免卡住）
        logger.warning(f"[搜索引擎] 所有搜索引擎均不可用，返回空结果")
        return []
    
    async def _search_tavily(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """调用 Tavily API"""
        timeout = aiohttp.ClientTimeout(total=5)  # 5秒超时（优化：减少等待时间）
        async with aiohttp.ClientSession(timeout=timeout) as session:
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
        timeout = aiohttp.ClientTimeout(total=5)  # 5秒超时（优化：减少等待时间）
        async with aiohttp.ClientSession(timeout=timeout) as session:
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
    
    def _score_domain(self, domain: str) -> float:
        normalized = (domain or "").lower().replace("www.", "")
        source_scores = {
            "bloomberg.com": 0.95,
            "reuters.com": 0.95,
            "federalreserve.gov": 0.98,
            "fred.stlouisfed.org": 0.98,
            "ecb.europa.eu": 0.95,
            "imf.org": 0.95,
            "worldbank.org": 0.93,
            "ft.com": 0.88,
            "cnbc.com": 0.8,
            "wallstreetcn.com": 0.8,
            "investing.com": 0.75,
            "marketwatch.com": 0.74,
            "seekingalpha.com": 0.6,
            "medium.com": 0.4,
        }
        for suffix, score in source_scores.items():
            if normalized == suffix or normalized.endswith(f".{suffix}"):
                return score
        if normalized.endswith(".gov"):
            return 0.9
        if normalized.endswith(".edu"):
            return 0.75
        return 0.3

    def _score_search_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scored = []
        for result in results:
            domain = result.get("domain") or urlparse(result.get("url", "")).netloc
            result["domain"] = domain
            result["source_quality_score"] = self._score_domain(domain)
            scored.append(result)
        return sorted(scored, key=lambda item: item.get("source_quality_score", 0.0), reverse=True)

    async def _search_single_query(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        cache_key = f"{query}:{max_results}"
        cached = self._search_cache.get(cache_key)
        if cached:
            cached_at, cached_results = cached
            if (datetime.utcnow() - cached_at).total_seconds() < self._search_cache_ttl_seconds:
                logger.info(f"[搜索缓存] 命中: {query}")
                return cached_results

        async def run_with_retries(provider_name, call):
            last_error = None
            for attempt in range(1, self.search_retry_attempts + 1):
                try:
                    results = await call()
                    scored_results = self._score_search_results(results)
                    self._search_cache[cache_key] = (datetime.utcnow(), scored_results)
                    return scored_results
                except Exception as e:
                    last_error = e
                    logger.warning(f"[搜索重试] {provider_name} 第 {attempt} 次失败: {str(e)}")
                    if attempt < self.search_retry_attempts:
                        await asyncio.sleep(min(2 ** (attempt - 1), 4))
            raise last_error

        if self.tavily_api_key:
            try:
                return await run_with_retries("Tavily", lambda: self._search_tavily(query, max_results))
            except Exception as e:
                logger.warning(f"[搜索引擎] Tavily 失败，尝试 Serper: {str(e)}")

        if self.serper_api_key:
            try:
                return await run_with_retries("Serper", lambda: self._search_serper(query, max_results))
            except Exception as e:
                logger.error(f"[搜索引擎] Serper 失败: {str(e)}")

        return []

    async def _search_tavily(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        timeout = aiohttp.ClientTimeout(total=self.search_timeout_seconds)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            payload = {
                "api_key": self.tavily_api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": min(max_results, 15),
            }
            async with session.post(self.tavily_base_url, json=payload) as resp:
                if resp.status != 200:
                    raise Exception(f"Tavily API returned {resp.status}")
                data = await resp.json()
                return [
                    {
                        "title": r.get("title", ""),
                        "snippet": r.get("content", ""),
                        "url": r.get("url", ""),
                        "domain": urlparse(r.get("url", "")).netloc,
                    }
                    for r in data.get("results", [])
                ]

    async def _search_serper(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        timeout = aiohttp.ClientTimeout(total=self.search_timeout_seconds)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            headers = {"X-API-KEY": self.serper_api_key, "Content-Type": "application/json"}
            payload = {"q": query, "num": min(max_results, 15)}
            async with session.post(self.serper_base_url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    raise Exception(f"Serper API returned {resp.status}")
                data = await resp.json()
                return [
                    {
                        "title": r.get("title", ""),
                        "snippet": r.get("snippet", ""),
                        "url": r.get("link", ""),
                        "domain": urlparse(r.get("link", "")).netloc,
                    }
                    for r in data.get("organic", [])
                ]

    def _filter_by_whitelist(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scored = self._score_search_results(search_results)
        if not self.whitelist_domains:
            return scored
        for result in scored:
            result["matched_whitelist"] = any(
                result.get("domain", "").endswith(domain) or result.get("domain", "") == domain
                for domain in self.whitelist_domains
            )
        return scored

    async def _extract_quantitative_state_stage1(
        self, 
        node_label: str, 
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Stage 1: 白名单直接提取（定量节点 - 提取具体数值）
        
        Args:
            node_label: 节点标签（如"美联储利率"）
            search_results: 白名单过滤后的搜索结果
            
        Returns:
            结构化状态对象: {value, trend, narrative_context, confidence, sources}
        """
        logger.info(f"[Stage 1 定量] 开始解析节点 '{node_label}' 的状态（白名单直接提取）")
        
        # 构建上下文
        context = self._build_search_context(search_results)
        
        # Stage 1 系统提示词：直接提取，信任白名单
        system_prompt = """你是一个专业的金融数据提取引擎。从权威来源快速提取关键数据。

【输出格式】JSON：
{
    "value": "具体数值或状态",
    "trend": "rising|falling|stable",
    "narrative_context": "一句话背景",
    "data_release_time": "YYYY年MM月DD日",
    "confidence": "whitelist_direct",
    "sources": [{"title": "标题", "url": "URL", "domain": "域名"}]
}

【规则】
1. value: 提取数值（如"5.25%"）或简短描述，无法确定则"unknown"
2. data_release_time: 提取数据发布时间（如"2024年12月18日"），无则"未知"
3. trend: rising/falling/stable
4. sources: 最多3条，包含title/url/domain
5. 信息不足时返回unknown"""

        user_prompt = f"""【节点名称】
{node_label}

【搜索结果（来自权威白名单域名）】
{context}

请提取该节点的实时状态，严格按照 JSON 格式输出。"""

        try:
            # 调用 LLM（优化：降低max_tokens加速）
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500,  # 限制输出长度，加快响应
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            state = json.loads(content)
            
            # 验证必需字段
            required_fields = ["value", "trend", "narrative_context", "data_release_time", "confidence", "sources"]
            for field in required_fields:
                if field not in state:
                    raise ValueError(f"LLM 返回缺少字段: {field}")
            
            # 验证 trend 枚举值
            valid_trends = ["rising", "falling", "stable"]
            if state["trend"] not in valid_trends:
                logger.warning(f"[Stage 1 定量] trend 值无效: {state['trend']}，修正为 stable")
                state["trend"] = "stable"
            
            logger.info(
                f"[Stage 1 定量] 节点 '{node_label}' 解析成功: "
                f"value={state['value']}, data_release_time={state.get('data_release_time', '未知')}, "
                f"sources={len(state.get('sources', []))}"
            )
            
            return state
            
        except Exception as e:
            logger.error(f"[Stage 1 定量] 节点 '{node_label}' 解析失败: {str(e)}")
            return self._create_unknown_state(confidence="whitelist_direct")
    
    async def _extract_qualitative_state_stage1(
        self, 
        node_label: str,
        node_type: str,
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Stage 1: 白名单直接提取（定性节点 - 提取情绪/风险等级）
        
        Args:
            node_label: 节点标签（如"地缘政治风险"）
            node_type: 节点类型（用于确定强度等级类型）
            search_results: 白名单过滤后的搜索结果
            
        Returns:
            结构化状态对象: {value, intensity, key_events, trend, narrative_context, confidence, sources}
        """
        logger.info(f"[Stage 1 定性] 开始解析节点 '{node_label}' 的状态（白名单直接提取）")
        
        # 获取强度等级类型
        intensity_scale = self._get_intensity_scale(node_type)
        intensity_options = self.intensity_levels.get(intensity_scale, self.intensity_levels.get("risk_based", []))
        
        # 构建上下文
        context = self._build_search_context(search_results)
        
        # Stage 1 定性节点系统提示词
        system_prompt = f"""你是金融情绪分析引擎。从权威来源快速提取风险/情绪状态。

【输出格式】JSON：
{{
    "value": "强度等级（从{intensity_options}中选择）",
    "intensity": 0.75,
    "key_events": ["事件1", "事件2"],
    "trend": "rising|falling|stable",
    "narrative_context": "一句话背景",
    "confidence": "whitelist_direct",
    "sources": [{{"title": "标题", "url": "URL", "domain": "域名"}}]
}}

【规则】
1. value: 从{intensity_options}选择，无法确定则"unknown"
2. intensity: 0.0-1.0评分
3. key_events: 1-3个关键事件（10-20字）
4. trend: rising/falling/stable
5. sources: 最多3条
6. 信息不足时返回unknown"""

        user_prompt = f"""【节点名称】
{node_label}

【节点类型】
{node_type}

【搜索结果（来自权威白名单域名）】
{context}

请分析该定性节点的当前状态，严格按照 JSON 格式输出。"""

        try:
            # 调用 LLM（优化：降低max_tokens加速）
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=500,  # 限制输出长度，加快响应
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            state = json.loads(content)
            
            # 验证必需字段
            required_fields = ["value", "intensity", "key_events", "trend", "narrative_context", "confidence", "sources"]
            for field in required_fields:
                if field not in state:
                    raise ValueError(f"LLM 返回缺少字段: {field}")
            
            # 验证 intensity 范围
            if not (0.0 <= state["intensity"] <= 1.0):
                logger.warning(f"[Stage 1 定性] intensity 值超出范围: {state['intensity']}，修正为 0.5")
                state["intensity"] = 0.5
            
            # 验证 trend 枚举值
            valid_trends = ["rising", "falling", "stable"]
            if state["trend"] not in valid_trends:
                logger.warning(f"[Stage 1 定性] trend 值无效: {state['trend']}，修正为 stable")
                state["trend"] = "stable"
            
            logger.info(
                f"[Stage 1 定性] 节点 '{node_label}' 解析成功: "
                f"value={state['value']}, intensity={state['intensity']}, "
                f"key_events={len(state.get('key_events', []))}"
            )
            
            return state
            
        except Exception as e:
            logger.error(f"[Stage 1 定性] 节点 '{node_label}' 解析失败: {str(e)}")
            return self._create_unknown_state(confidence="whitelist_direct", intensity=0.5)
    
    async def _extract_quantitative_state_simple(
        self, 
        node_label: str, 
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        简化版全网提取（定量节点）- 不要求严格三方验证
        
        Args:
            node_label: 节点标签
            search_results: 全网搜索结果
            
        Returns:
            结构化状态对象: {value, trend, narrative_context, confidence, sources}
        """
        logger.info(f"[简化提取] 定量节点: {node_label}")
        
        # 构建上下文
        context = self._build_search_context(search_results)
        
        # 简化版系统提示词（不要求严格验证）
        system_prompt = """你是金融数据提取专家。从搜索结果中提取最新数据。

【输出格式】JSON：
{
    "value": "具体数值或状态",
    "trend": "rising|falling|stable",
    "narrative_context": "一句话背景",
    "data_release_time": "YYYY年MM月DD日",
    "confidence": "web_search",
    "sources": [{"title": "标题", "url": "URL", "domain": "域名"}]
}

【规则】
1. value: 提取最常见的数值，无法确定则"unknown"
2. data_release_time: 提取发布时间，无则"未知"
3. trend: rising/falling/stable
4. sources: 列出1-3个支持该数值的来源
5. 优先选择权威来源（bloomberg/reuters/cnbc等）"""

        user_prompt = f"""【节点】{node_label}

【搜索结果】
{context}

提取最新状态。"""

        try:
            # 调用 LLM（优化：降低max_tokens加速）
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            
            # 尝试解析JSON，如果失败则记录详细信息
            try:
                state = json.loads(content)
            except json.JSONDecodeError as json_err:
                logger.error(f"[简化提取] 定量节点 '{node_label}' JSON解析失败: {json_err}")
                logger.debug(f"[简化提取] LLM返回内容: {content[:500]}")  # 只记录前500字符
                return self._create_unknown_state(confidence="web_search")
            
            # 验证必需字段
            required_fields = ["value", "trend", "narrative_context", "data_release_time", "confidence", "sources"]
            for field in required_fields:
                if field not in state:
                    logger.warning(f"[简化提取] 定量节点 '{node_label}' 缺少字段: {field}")
                    raise ValueError(f"LLM 返回缺少字段: {field}")
            
            # 验证 trend 枚举值
            valid_trends = ["rising", "falling", "stable"]
            if state["trend"] not in valid_trends:
                state["trend"] = "stable"
            
            logger.info(f"[简化提取] 定量节点 '{node_label}' 完成: value={state['value']}")
            
            return state
            
        except Exception as e:
            logger.error(f"[简化提取] 定量节点 '{node_label}' 失败: {str(e)}")
            return self._create_unknown_state(confidence="web_search")
    
    async def _extract_qualitative_state_simple(
        self, 
        node_label: str,
        node_type: str,
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        简化版全网提取（定性节点）- 不要求严格多源验证
        
        Args:
            node_label: 节点标签
            node_type: 节点类型
            search_results: 全网搜索结果
            
        Returns:
            结构化状态对象: {value, intensity, key_events, trend, narrative_context, confidence, sources}
        """
        logger.info(f"[简化提取] 定性节点: {node_label}")
        
        # 获取强度等级类型
        intensity_scale = self._get_intensity_scale(node_type)
        intensity_options = self.intensity_levels.get(intensity_scale, self.intensity_levels.get("risk_based", []))
        
        # 构建上下文
        context = self._build_search_context(search_results)
        
        # 简化版系统提示词（不要求严格验证）
        system_prompt = f"""你是金融情绪分析专家。从搜索结果中提取风险/情绪状态。

【输出格式】JSON：
{{
    "value": "强度等级（从{intensity_options}中选择）",
    "intensity": 0.75,
    "key_events": ["事件1", "事件2"],
    "trend": "rising|falling|stable",
    "narrative_context": "一句话背景",
    "confidence": "web_search",
    "sources": [{{"title": "标题", "url": "URL", "domain": "域名"}}]
}}

【规则】
1. value: 从{intensity_options}选择最合适的等级
2. intensity: 0.0-1.0评分
3. key_events: 1-3个关键事件（10-20字）
4. trend: rising/falling/stable
5. sources: 列出1-3个来源
6. 优先选择权威来源"""

        user_prompt = f"""【节点】{node_label}
【类型】{node_type}

【搜索结果】
{context}

提取当前状态。"""

        try:
            # 调用 LLM（优化：降低max_tokens加速）
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            
            # 尝试解析JSON，如果失败则记录详细信息
            try:
                state = json.loads(content)
            except json.JSONDecodeError as json_err:
                logger.error(f"[简化提取] 定性节点 '{node_label}' JSON解析失败: {json_err}")
                logger.debug(f"[简化提取] LLM返回内容: {content[:500]}")  # 只记录前500字符
                return self._create_unknown_state(confidence="web_search", intensity=0.5)
            
            # 验证必需字段
            required_fields = ["value", "intensity", "key_events", "trend", "narrative_context", "confidence", "sources"]
            for field in required_fields:
                if field not in state:
                    logger.warning(f"[简化提取] 定性节点 '{node_label}' 缺少字段: {field}")
                    raise ValueError(f"LLM 返回缺少字段: {field}")
            
            # 验证 intensity 范围
            if not (0.0 <= state["intensity"] <= 1.0):
                state["intensity"] = 0.5
            
            # 验证 trend 枚举值
            valid_trends = ["rising", "falling", "stable"]
            if state["trend"] not in valid_trends:
                state["trend"] = "stable"
            
            logger.info(f"[简化提取] 定性节点 '{node_label}' 完成: value={state['value']}")
            
            return state
            
        except Exception as e:
            logger.error(f"[简化提取] 定性节点 '{node_label}' 失败: {str(e)}")
            return self._create_unknown_state(confidence="web_search", intensity=0.5)
    
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
        narrative: str = "暂无足够信息判断当前状态",
        intensity: Optional[float] = None
    ) -> Dict[str, Any]:
        """创建 unknown 状态（降级方案）"""
        state = {
            "value": "unknown",
            "trend": "stable",
            "narrative_context": narrative,
            "data_release_time": "未知",
            "confidence": confidence,
            "sources": []
        }
        
        # 如果是定性节点，添加 intensity 和 key_events 字段
        if intensity is not None:
            state["intensity"] = intensity
            state["key_events"] = []
        
        return state
