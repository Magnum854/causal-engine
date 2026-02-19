import yfinance as yf
import asyncio
from app.services.yahoo_finance_service import YahooFinanceService

async def test_yahoo_finance():
    print("=" * 60)
    print("测试 Yahoo Finance 直连")
    print("=" * 60)
    
    # 测试 1: 直接使用 yfinance
    print("\n[测试 1] 直接调用 yfinance")
    try:
        ticker = yf.Ticker("GC=F")
        info = ticker.info
        price = info.get("regularMarketPrice") or info.get("currentPrice")
        currency = info.get("currency", "USD")
        print(f"成功 黄金价格: {price} {currency}")
    except Exception as e:
        print(f"失败: {e}")
    
    # 测试 2: 使用 YahooFinanceService
    print("\n[测试 2] 使用 YahooFinanceService")
    service = YahooFinanceService()
    
    # 测试匹配
    print("\n匹配测试:")
    test_labels = ["黄金价格", "美元指数", "比特币", "标普500"]
    for label in test_labels:
        ticker = service.match_ticker(label)
        print(f"  {label} -> {ticker}")
    
    # 测试获取数据
    print("\n数据获取测试:")
    result = await service.fetch_by_node_label("黄金价格")
    if result:
        print(f"成功获取数据:")
        print(f"  - 最新值: {result['latest_value']}")
        print(f"  - 趋势: {result['trend']}")
        print(f"  - 涨跌幅: {result['change_percent']}")
        print(f"  - 数据源: {result['sources'][0]['url']}")
    else:
        print("未能获取数据")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_yahoo_finance())

