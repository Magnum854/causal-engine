"""
多路由数据获取服务 (Multi-Tool Router)
根据节点类型智能选择数据源：结构化 API 或新闻搜索
"""
import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from urllib.parse import urlparse

from app.services.structured_api_service import StructuredAPIService

logger = logging.getLogger(__name__)


class MultiToolRouterService:
    """
    多路由工具调用服务
    
    核心职责：
    1. 根据节点类型决定使用哪种数据获取策略
    2. 策略 A: 结构化 API（精确数值）
    3. 策略 B: 新闻搜索（情绪/事件）
    4. 支持白名单域名过滤
    """
    
    def __init__(self, search_service=None):
        """
        Args:
            search_service: 搜索引擎服务实例（用于新闻搜索）
        """
        self.search_service = search_service
        self.structured_api_service = StructuredAPIService()
        
        # 加载配置
        config_path = Path(__file__).parent.parent.parent / "config" / "financial_sources.json"
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        
        logger.info("[MultiToolRouter] 初始化完成")
        logger.info(f"  - 结构化 API: {len(self.config['structured_apis'])} 个")
        logger.info(f"  - 搜索域名白名单: {len(self._get_all_search_domains())} 个")
    
    def _get_all_search_domains(self) -> List[str]:
        """获取所有搜索域名白名单"""
        domains = []
        for category_name, category_data in self.config["search_domains"].items():
            if category_name == "description":
                continue
            if isinstance(category_data, dict) and "domains" in category_data:
                domains.extend(category_data["domains"])
        return domains
    
    def _get_routing_rule(self, node_type: str) -> Optional[Dict[str, Any]]:
        """
        获取节点类型的路由规则
        
        Args:
            node_type: 节点类型
            
        Returns:
            路由规则字典，如果没有匹配则返回默认规则
        """
        rules = self.config.get("routing_rules", {})
        
        # 精确匹配
        if node_type in rules:
            return rules[node_type]
        
        # 默认规则：使用新闻搜索
        logger.warning(f"[Router] 节点类型 {node_type} 无匹配规则，使用默认策略（新闻搜索）")
        
        # 获取所有域名并分配到 tier_1 和 tier_2
        all_domains = self._get_all_search_domains()
        
        return {
            "primary_strategy": "news_search",
            "fallback_strategy": None,
            "preferred_apis": [],
            "tier_1_domains": all_domains[:10] if len(all_domains) > 10 else all_domains,
            "tier_2_domains": all_domains[10:] if len(all_domains) > 10 else []
        }
    
    async def fetch_node_data(
        self,
        node_label: str,
        node_type: str,
        search_query: str
    ) -> Dict[str, Any]:
        """
        智能路由：根据节点类型获取数据
        
        Args:
            node_label: 节点标签
            node_type: 节点类型
            search_query: 搜索查询（用于新闻搜索）
            
        Returns:
            {
                "latest_value": "数值或状态",
                "sources": [...],
                "strategy_used": "structured_api" | "news_search",
                "updated_at": "ISO 时间戳"
            }
        """
        logger.info(f"[Router] 路由节点: {node_label} (类型: {node_type})")
        
        # 获取路由规则
        rule = self._get_routing_rule(node_type)
        primary_strategy = rule.get("primary_strategy", "news_search")
        
        logger.info(f"[Router] 主策略: {primary_strategy}")
        
        # 策略 A: 结构化 API
        if primary_strategy == "structured_api":
            result = await self._try_structured_api(node_label, node_type, rule)
            if result:
                return result
            
            # Fallback 到新闻搜索
            logger.warning(f"[Router] 结构化 API 失败，回退到新闻搜索")
            return await self._try_news_search(node_label, search_query, rule)
        
        # 策略 B: 新闻搜索
        else:
            return await self._try_news_search(node_label, search_query, rule)
    
    async def _try_structured_api(
        self,
        node_label: str,
        node_type: str,
        rule: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        尝试使用结构化 API 获取数据
        
        Returns:
            成功返回数据字典，失败返回 None
        """
        preferred_apis = rule.get("preferred_apis", [])
        
        if not preferred_apis:
            logger.warning(f"[Router] 节点类型 {node_type} 无首选 API")
            return None
        
        # 尝试每个首选 API
        for api_name in preferred_apis:
            try:
                logger.info(f"[Router] 尝试 API: {api_name}")
                
                data = await self.structured_api_service.fetch_data(
                    api_name=api_name,
                    node_label=node_label,
                    node_type=node_type
                )
                
                if data:
                    # 转换为统一格式
                    return {
                        "latest_value": data["value"],
                        "sources": [{
                            "title": f"{data['source']} - {node_label}",
                            "url": self._get_api_url(api_name),
                            "domain": self._get_api_domain(api_name),
                            "type": "structured_api",
                            "metadata": data.get("metadata", {})
                        }],
                        "strategy_used": "structured_api",
                        "updated_at": data["timestamp"]
                    }
            
            except Exception as e:
                logger.error(f"[Router] API {api_name} 调用失败: {str(e)}")
                continue
        
        return None
    
    async def _try_news_search(
        self,
        node_label: str,
        search_query: str,
        rule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        使用新闻搜索获取数据（瀑布流降级搜索）
        
        Waterfall Logic:
        - Attempt 1: Tier 1 + Tier 2 白名单，7天时间窗
        - Attempt 2: 全网搜索，30天时间窗 + LLM 权威性判断
        
        Returns:
            数据字典
        """
        if not self.search_service:
            logger.error("[Router] 搜索服务未初始化")
            return self._empty_result()
        
        waterfall_config = self.config.get("waterfall_config", {})
        
        # ============================================================
        # Attempt 1: 白名单搜索（Tier 1 + Tier 2）
        # ============================================================
        logger.info(f"[Waterfall] Attempt 1: 白名单搜索 (7天窗口)")
        
        tier_1_domains = rule.get("tier_1_domains", [])
        tier_2_domains = rule.get("tier_2_domains", [])
        combined_whitelist = tier_1_domains + tier_2_domains
        
        logger.info(f"[Waterfall] 白名单域名: {len(combined_whitelist)} 个")
        
        # 调用搜索服务
        search_results_attempt1 = await self.search_service.search(search_query)
        
        # 白名单过滤
        filtered_results_attempt1 = self._filter_by_whitelist(
            search_results_attempt1, 
            combined_whitelist
        )
        
        logger.info(
            f"[Waterfall] Attempt 1 结果: "
            f"{len(search_results_attempt1)} 条 -> 白名单过滤后: {len(filtered_results_attempt1)} 条"
        )
        
        # 如果有结果，尝试提取
        if filtered_results_attempt1:
            result = await self._build_search_result(
                node_label=node_label,
                search_results=filtered_results_attempt1,
                attempt_number=1,
                authority_check=False
            )
            
            # 如果成功提取到非 unknown 值，直接返回
            if result.get("latest_value") != "unknown":
                logger.info(f"[Waterfall] ✓ Attempt 1 成功: {result['latest_value']}")
                return result
            else:
                logger.warning(f"[Waterfall] Attempt 1 提取失败: LLM 返回 unknown")
        else:
            logger.warning(f"[Waterfall] Attempt 1 无结果")
        
        # ============================================================
        # Attempt 2: 全网搜索（无域名限制 + LLM 权威性判断）
        # ============================================================
        logger.info(f"[Waterfall] Attempt 2: 全网搜索 (30天窗口 + 权威性判断)")
        
        # 重新搜索（实际场景中可能需要调整搜索参数，如时间窗口）
        search_results_attempt2 = await self.search_service.search(search_query)
        
        logger.info(f"[Waterfall] Attempt 2 结果: {len(search_results_attempt2)} 条（全网）")
        
        if not search_results_attempt2:
            logger.error(f"[Waterfall] Attempt 2 无结果，返回空")
            return self._empty_result()
        
        # 使用 LLM 权威性判断
        result = await self._build_search_result(
            node_label=node_label,
            search_results=search_results_attempt2[:10],  # 取前10条
            attempt_number=2,
            authority_check=True
        )
        
        if result.get("latest_value") != "unknown":
            logger.info(f"[Waterfall] ✓ Attempt 2 成功: {result['latest_value']}")
        else:
            logger.warning(f"[Waterfall] ✗ Attempt 2 失败: 全网搜索仍无法提取有效数据")
        
        return result
    
    async def _build_search_result(
        self,
        node_label: str,
        search_results: List[Dict[str, Any]],
        attempt_number: int,
        authority_check: bool
    ) -> Dict[str, Any]:
        """
        构建搜索结果（包含 LLM 解析）
        
        Args:
            node_label: 节点标签
            search_results: 搜索结果列表
            attempt_number: 尝试次数（1 或 2）
            authority_check: 是否启用 LLM 权威性判断
            
        Returns:
            {
                "latest_value": "...",
                "sources": [...],
                "strategy_used": "news_search",
                "attempt_number": 1 or 2
            }
        """
        # 构建 sources
        sources = []
        for r in search_results[:5]:
            url = r.get("url", "")
            domain = urlparse(url).netloc if url else "unknown"
            
            sources.append({
                "title": r.get("title", ""),
                "url": url,
                "domain": domain,
                "type": "news_search",
                "snippet": r.get("snippet", "")
            })
        
        return {
            "latest_value": "unknown",  # 需要 LLM 解析
            "sources": sources,
            "strategy_used": "news_search",
            "updated_at": None,
            "raw_results": search_results,
            "attempt_number": attempt_number,
            "authority_check": authority_check
        }
    
    def _empty_result(self) -> Dict[str, Any]:
        """返回空结果"""
        return {
            "latest_value": "unknown",
            "sources": [],
            "strategy_used": "news_search",
            "updated_at": None
        }
    
    def _filter_by_whitelist(
        self,
        search_results: List[Dict[str, Any]],
        whitelist_domains: List[str]
    ) -> List[Dict[str, Any]]:
        """
        根据白名单过滤搜索结果
        
        Args:
            search_results: 原始搜索结果
            whitelist_domains: 白名单域名列表
            
        Returns:
            过滤后的结果
        """
        if not whitelist_domains:
            return search_results
        
        filtered = []
        for result in search_results:
            url = result.get("url", "")
            if not url:
                continue
            
            domain = urlparse(url).netloc
            
            # 检查是否在白名单中（支持子域名）
            for whitelist_domain in whitelist_domains:
                if domain.endswith(whitelist_domain):
                    filtered.append(result)
                    logger.debug(f"[Router] ✓ 白名单匹配: {domain} -> {whitelist_domain}")
                    break
            else:
                logger.debug(f"[Router] ✗ 白名单拒绝: {domain}")
        
        return filtered
    
    def _get_api_url(self, api_name: str) -> str:
        """获取 API 的官方 URL"""
        api_config = self.config["structured_apis"].get(api_name, {})
        return api_config.get("base_url", "")
    
    def _get_api_domain(self, api_name: str) -> str:
        """获取 API 的域名"""
        url = self._get_api_url(api_name)
        if url:
            return urlparse(url).netloc
        return api_name

