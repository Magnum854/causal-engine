"""
Yahoo Finance 直连服务 (Direct API Bypass)
用于绕过付费墙，直接获取资产价格和宏观指标的实时数据
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import yfinance as yf

logger = logging.getLogger(__name__)


class YahooFinanceService:
    """
    Yahoo Finance 直连服务
    
    核心功能：
    1. 提供 Ticker 映射字典（中英文资产名称 -> Yahoo Ticker）
    2. 直接调用 yfinance 获取实时价格
    3. 自动计算趋势（rising/falling/stable）
    4. 返回标准化的 realtime_state 格式
    """
    
    # Ticker 映射字典（常见宏观资产和金融指标）
    TICKER_MAPPING = {
        # 贵金属
        "黄金": "GC=F",
        "黄金价格": "GC=F",
        "gold": "GC=F",
        "gold price": "GC=F",
        "白银": "SI=F",
        "silver": "SI=F",
        
        # 外汇与指数
        "美元指数": "DX-Y.NYB",
        "us dollar index": "DX-Y.NYB",
        "dxy": "DX-Y.NYB",
        "人民币汇率": "CNY=X",
        "usdcny": "CNY=X",
        
        # 债券收益率
        "美国十年期国债": "^TNX",
        "美国十年期国债收益率": "^TNX",
        "us 10y treasury": "^TNX",
        "10y treasury": "^TNX",
        "美国两年期国债": "^IRX",
        "us 2y treasury": "^IRX",
        
        # 能源
        "原油": "CL=F",
        "原油价格": "CL=F",
        "crude oil": "CL=F",
        "wti": "CL=F",
        "布伦特原油": "BZ=F",
        "brent crude": "BZ=F",
        "天然气": "NG=F",
        "natural gas": "NG=F",
        
        # 股票指数
        "标普500": "^GSPC",
        "s&p 500": "^GSPC",
        "sp500": "^GSPC",
        "纳斯达克": "^IXIC",
        "nasdaq": "^IXIC",
        "道琼斯": "^DJI",
        "dow jones": "^DJI",
        "上证指数": "000001.SS",
        "上证综指": "000001.SS",
        "shanghai composite": "000001.SS",
        
        # 加密货币
        "比特币": "BTC-USD",
        "bitcoin": "BTC-USD",
        "btc": "BTC-USD",
        "以太坊": "ETH-USD",
        "ethereum": "ETH-USD",
        "eth": "ETH-USD",
        
        # 大宗商品
        "铜": "HG=F",
        "copper": "HG=F",
        "铝": "ALI=F",
        "aluminum": "ALI=F",
        "大豆": "ZS=F",
        "soybeans": "ZS=F",
        "玉米": "ZC=F",
        "corn": "ZC=F",
    }
    
    def __init__(self):
        logger.info(f"[YahooFinance] 初始化完成，支持 {len(self.TICKER_MAPPING)} 个资产映射")
    
    def match_ticker(self, node_label: str) -> Optional[str]:
        """
        匹配节点标签到 Yahoo Finance Ticker
        
        Args:
            node_label: 节点标签（如 "黄金价格", "美元指数"）
            
        Returns:
            匹配的 Ticker（如 "GC=F"），未匹配返回 None
        """
        node_label_lower = node_label.lower().strip()
        
        # 精确匹配
        if node_label_lower in self.TICKER_MAPPING:
            ticker = self.TICKER_MAPPING[node_label_lower]
            logger.info(f"[YahooFinance] ✓ 精确匹配: {node_label} -> {ticker}")
            return ticker
        
        # 模糊匹配（包含关系）
        for key, ticker in self.TICKER_MAPPING.items():
            if key in node_label_lower or node_label_lower in key:
                logger.info(f"[YahooFinance] ✓ 模糊匹配: {node_label} -> {ticker} (via {key})")
                return ticker
        
        logger.debug(f"[YahooFinance] ✗ 未匹配: {node_label}")
        return None
    
    async def fetch_financial_data(
        self, 
        ticker: str,
        node_label: str = "",
        max_retries: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        获取金融资产的实时数据（带重试和延迟）
        
        Args:
            ticker: Yahoo Finance Ticker（如 "GC=F"）
            node_label: 节点标签（用于日志）
            max_retries: 最大重试次数
            
        Returns:
            金融数据字典或 None
        """
        import asyncio
        
        logger.info(f"[YahooFinance] 获取数据: {ticker} ({node_label})")
        
        for attempt in range(max_retries):
            try:
                # 添加延迟避免速率限制（第一次请求不延迟）
                if attempt > 0:
                    delay = 2 ** attempt  # 指数退避: 2s, 4s, 8s
                    logger.info(f"[YahooFinance] 重试 {attempt + 1}/{max_retries}，等待 {delay}秒")
                    await asyncio.sleep(delay)
                
                # 调用 yfinance
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # 获取当前价格
                current_price = info.get("regularMarketPrice") or info.get("currentPrice")
                if current_price is None:
                    if attempt < max_retries - 1:
                        logger.warning(f"[YahooFinance] 无法获取价格: {ticker}，将重试")
                        continue
                    else:
                        logger.warning(f"[YahooFinance] 无法获取价格: {ticker}，已达最大重试次数")
                        return None
                
                # 获取昨日收盘价
                previous_close = info.get("regularMarketPreviousClose") or info.get("previousClose")
                
                # 计算趋势
                trend = "stable"
                change_percent = "0.00%"
                if previous_close and previous_close > 0:
                    change = current_price - previous_close
                    change_pct = (change / previous_close) * 100
                    
                    if change_pct > 0.1:
                        trend = "rising"
                    elif change_pct < -0.1:
                        trend = "falling"
                    
                    change_percent = f"{change_pct:+.2f}%"
                
                # 获取货币单位
                currency = info.get("currency", "USD")
                
                # 获取资产名称
                asset_name = info.get("shortName") or info.get("longName") or ticker
                
                # 构建标准化结果
                result = {
                    "latest_value": f"{current_price:.2f} {currency}",
                    "trend": trend,
                    "change_percent": change_percent,
                    "previous_close": f"{previous_close:.2f}" if previous_close else "N/A",
                    "sources": [{
                        "title": f"Yahoo Finance - {asset_name}",
                        "url": f"https://finance.yahoo.com/quote/{ticker}",
                        "domain": "finance.yahoo.com",
                        "type": "direct_api"
                    }],
                    "updated_at": datetime.utcnow().isoformat(),
                    "metadata": {
                        "ticker": ticker,
                        "currency": currency,
                        "market_state": info.get("marketState", "UNKNOWN"),
                        "asset_name": asset_name
                    }
                }
                
                logger.info(
                    f"[YahooFinance] ✓ 成功: {ticker} = {result['latest_value']} "
                    f"({result['trend']}, {result['change_percent']})"
                )
                
                return result
                
            except Exception as e:
                error_msg = str(e)
                
                # 检查是否是 429 错误
                if "429" in error_msg or "Too Many Requests" in error_msg:
                    if attempt < max_retries - 1:
                        delay = 2 ** (attempt + 1)
                        logger.warning(f"[YahooFinance] 速率限制 (429): {ticker}，将在 {delay}秒后重试")
                        continue
                    else:
                        logger.error(f"[YahooFinance] 速率限制 (429): {ticker}，已达最大重试次数")
                        return None
                else:
                    logger.error(f"[YahooFinance] 获取失败: {ticker} - {error_msg}")
                    if attempt < max_retries - 1:
                        continue
                    return None
        
        # 所有重试都失败
        logger.error(f"[YahooFinance] 所有重试失败: {ticker}")
        return None
    
    async def fetch_by_node_label(self, node_label: str) -> Optional[Dict[str, Any]]:
        """
        根据节点标签直接获取数据（自动匹配 Ticker）
        
        Args:
            node_label: 节点标签
            
        Returns:
            金融数据字典，未匹配返回 None
        """
        ticker = self.match_ticker(node_label)
        if not ticker:
            return None
        
        return await self.fetch_financial_data(ticker, node_label)

