"""测试 .env 文件读取"""
import os
from dotenv import load_dotenv

print("=" * 60)
print("环境变量测试")
print("=" * 60)

# 加载 .env 文件
load_dotenv()

# 检查关键环境变量
env_vars = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL"),
    "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY"),
    "SERPER_API_KEY": os.getenv("SERPER_API_KEY"),
}

print("\n读取到的环境变量：")
print("-" * 60)
for key, value in env_vars.items():
    if value:
        # 只显示前10个字符，保护隐私
        masked_value = value[:10] + "..." if len(value) > 10 else value
        print(f"✅ {key} = {masked_value}")
    else:
        print(f"❌ {key} = None (未配置)")

print("-" * 60)

# 判断是否会使用 Mock 模式
tavily_key = os.getenv("TAVILY_API_KEY")
serper_key = os.getenv("SERPER_API_KEY")
use_mock = not (tavily_key or serper_key)

print(f"\n搜索引擎状态：")
if use_mock:
    print("❌ 将使用 Mock 模式（未配置 Tavily 或 Serper API）")
else:
    if tavily_key:
        print("✅ 将使用 Tavily API")
    elif serper_key:
        print("✅ 将使用 Serper API")

print("=" * 60)

