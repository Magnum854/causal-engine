"""
搜索工具服务
支持多种搜索引擎 API 集成
"""

import os
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
import json

class SearchService:
    """搜索服务 - 支持多种搜索引擎"""
    
    def __init__(self):
        # 支持的搜索引擎配置
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        
        # 默认使用的搜索引擎
        self.default_engine = os.getenv("SEARCH_ENGINE", "tavily")
        
        # 超时设置
        self.timeout = 30
    
    async def _search_tavily(self, query: str) -> List[Dict[str, Any]]:
        """
        使用 Tavily Search API
        https://tavily.com/
        """
        if not self.tavily_api_key:
            raise ValueError("TAVILY_API_KEY 未配置")
        
        url = "https://api.tavily.com/search"
        
        payload = {
            "api_key": self.tavily_api_key,
            "query": query,
            "search_depth": "advanced",
            "max_results": 5,
            "include_answer": True,
            "include_raw_content": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=self.timeout) as response:
                if response.status != 200:
                    raise Exception(f"Tavily API 错误: {response.status}")
                
                data = await response.json()
                
                # 提取搜索结果
                results = []
                for item in data.get("results", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("content", ""),
                        "score": item.get("score", 0)
                    })
                
                return results
    
    async def _search_serper(self, query: str) -> List[Dict[str, Any]]:
        """
        使用 Serper.dev API
        https://serper.dev/
        """
        if not self.serper_api_key:
            raise ValueError("SERPER_API_KEY 未配置")
        
        url = "https://google.serper.dev/search"
        
        headers = {
            "X-API-KEY": self.serper_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "num": 5,
            "gl": "cn",  # 中国地区
            "hl": "zh-cn"  # 中文
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=self.timeout) as response:
                if response.status != 200:
                    raise Exception(f"Serper API 错误: {response.status}")
                
                data = await response.json()
                
                # 提取搜索结果
                results = []
                for item in data.get("organic", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "position": item.get("position", 0)
                    })
                
                return results
    
    async def _search_duckduckgo(self, query: str) -> List[Dict[str, Any]]:
        """
        使用 DuckDuckGo (免费，无需 API Key)
        注意：这是一个简化实现，生产环境建议使用 duckduckgo-search 库
        """
        # 这里预留接口，实际使用时需要安装 duckduckgo-search
        # pip install duckduckgo-search
        
        try:
            from duckduckgo_search import DDGS
            
            results = []
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=5)
                for item in search_results:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("href", ""),
                        "snippet": item.get("body", "")
                    })
            
            return results
        except ImportError:
            raise Exception("DuckDuckGo 搜索需要安装 duckduckgo-search 库")
    
    async def search_single(self, query: str, engine: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        执行单个搜索查询
        
        Args:
            query: 搜索关键词
            engine: 搜索引擎 (tavily, serper, duckduckgo)
            
        Returns:
            搜索结果列表
        """
        engine = engine or self.default_engine
        
        try:
            if engine == "tavily":
                return await self._search_tavily(query)
            elif engine == "serper":
                return await self._search_serper(query)
            elif engine == "duckduckgo":
                return await self._search_duckduckgo(query)
            else:
                raise ValueError(f"不支持的搜索引擎: {engine}")
        except Exception as e:
            print(f"搜索失败 [{query}]: {str(e)}")
            return []
    
    async def perform_search(self, queries: List[str], engine: Optional[str] = None) -> str:
        """
        并发执行多个搜索查询，合并结果
        
        Args:
            queries: 搜索关键词列表
            engine: 搜索引擎
            
        Returns:
            合并后的搜索结果文本
        """
        if not queries:
            return ""
        
        print(f"开始并发搜索，共 {len(queries)} 个查询...")
        
        # 并发执行所有搜索
        tasks = [self.search_single(query, engine) for query in queries]
        all_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并所有搜索结果
        context_parts = []
        
        for i, (query, results) in enumerate(zip(queries, all_results), 1):
            if isinstance(results, Exception):
                print(f"查询 {i} 失败: {query} - {str(results)}")
                continue
            
            if not results:
                print(f"查询 {i} 无结果: {query}")
                continue
            
            # 添加查询标题
            context_parts.append(f"\n【搜索查询 {i}: {query}】\n")
            
            # 添加每个搜索结果
            for j, item in enumerate(results, 1):
                title = item.get("title", "无标题")
                snippet = item.get("snippet", "")
                url = item.get("url", "")
                
                context_parts.append(f"{j}. {title}")
                if snippet:
                    context_parts.append(f"   {snippet}")
                if url:
                    context_parts.append(f"   来源: {url}")
                context_parts.append("")
        
        # 合并成一个长字符串
        context = "\n".join(context_parts)
        
        print(f"搜索完成，获取到 {len(context)} 字符的上下文")
        
        return context
    
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """
        格式化搜索结果为可读文本
        """
        if not results:
            return "未找到相关信息"
        
        formatted = []
        for i, item in enumerate(results, 1):
            formatted.append(f"{i}. {item.get('title', '无标题')}")
            if item.get('snippet'):
                formatted.append(f"   {item['snippet']}")
            formatted.append("")
        
        return "\n".join(formatted)








