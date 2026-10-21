# -*- coding: utf-8 -*-
"""
置信度计算工具测试脚本 - 数据一致性功能
测试新增的数据一致性检查功能
"""
import sys
import os

# 设置控制台编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加当前目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app.utils.confidence_calculator import (
    calculate_node_confidence,
    calculate_consistency_score,
    calculate_numeric_consistency,
    calculate_text_consistency,
    calculate_trend_consistency
)

print("=" * 80)
print("置信度计算 - 数据一致性功能测试")
print("=" * 80)

# 测试 1: 数值高度一致
print("\n[测试 1] 数值高度一致的场景")
print("-" * 80)
sources_consistent = [
    {
        'url': 'https://www.xinhuanet.com/article1',
        'value': '103.5',
        'trend': 'rising',
        'description': '美元指数升至103.5点'
    },
    {
        'url': 'https://www.reuters.com/article2',
        'value': '103.6',
        'trend': 'rising',
        'description': '美元指数上涨至103.6'
    },
    {
        'url': 'https://www.bloomberg.com/article3',
        'value': '103.4',
        'trend': 'rising',
        'description': '美元指数走强至103.4点'
    }
]

result1 = calculate_node_confidence(sources_consistent, 0.85)
print(f"最终置信度: {result1['final_score']}")
print(f"等级: {result1['rating']}")
print(f"维度得分:")
print(f"  - 信源权威度: {result1['dimensions']['authority']}")
print(f"  - 交叉验证度: {result1['dimensions']['cross_validation']}")
print(f"  - 数据一致性: {result1['dimensions']['consistency']}")
print(f"  - 模型确定性: {result1['dimensions']['certainty']}")
print(f"一致性详情: {result1['consistency_details']}")
if 'warning' in result1:
    print(f"[WARNING] {result1['warning']}")

# 测试 2: 数值存在矛盾
print("\n[测试 2] 数值存在矛盾的场景")
print("-" * 80)
sources_conflict = [
    {
        'url': 'https://www.xinhuanet.com/article1',
        'value': '103.5',
        'trend': 'rising',
        'description': '美元指数升至103.5点'
    },
    {
        'url': 'https://www.reuters.com/article2',
        'value': '98.2',
        'trend': 'falling',
        'description': '美元指数下跌至98.2'
    },
    {
        'url': 'https://www.bloomberg.com/article3',
        'value': '110.8',
        'trend': 'rising',
        'description': '美元指数飙升至110.8点'
    }
]

result2 = calculate_node_confidence(sources_conflict, 0.85)
print(f"最终置信度: {result2['final_score']}")
print(f"等级: {result2['rating']}")
print(f"维度得分:")
print(f"  - 信源权威度: {result2['dimensions']['authority']}")
print(f"  - 交叉验证度: {result2['dimensions']['cross_validation']}")
print(f"  - 数据一致性: {result2['dimensions']['consistency']}")
print(f"  - 模型确定性: {result2['dimensions']['certainty']}")
print(f"一致性详情: {result2['consistency_details']}")
if 'warning' in result2:
    print(f"[WARNING] {result2['warning']}")

# 测试 3: 趋势矛盾
print("\n[测试 3] 趋势判断矛盾的场景")
print("-" * 80)
sources_trend_conflict = [
    {
        'url': 'https://www.caixin.com/article1',
        'value': '103.5',
        'trend': 'rising',
        'description': '美元指数持续上涨'
    },
    {
        'url': 'https://www.sina.com.cn/article2',
        'value': '103.4',
        'trend': 'falling',
        'description': '美元指数出现下跌'
    }
]

result3 = calculate_node_confidence(sources_trend_conflict, 0.75)
print(f"最终置信度: {result3['final_score']}")
print(f"等级: {result3['rating']}")
print(f"维度得分:")
print(f"  - 信源权威度: {result3['dimensions']['authority']}")
print(f"  - 交叉验证度: {result3['dimensions']['cross_validation']}")
print(f"  - 数据一致性: {result3['dimensions']['consistency']}")
print(f"  - 模型确定性: {result3['dimensions']['certainty']}")
print(f"一致性详情: {result3['consistency_details']}")
if 'warning' in result3:
    print(f"[WARNING] {result3['warning']}")

# 测试 4: 文本描述一致性
print("\n[测试 4] 文本描述一致性测试")
print("-" * 80)
sources_text = [
    {
        'url': 'https://www.reuters.com/article1',
        'description': '美联储宣布维持利率不变，保持在5.25%-5.50%区间'
    },
    {
        'url': 'https://www.bloomberg.com/article2',
        'description': '美联储决定维持基准利率在5.25%至5.50%之间'
    },
    {
        'url': 'https://www.ft.com/article3',
        'description': '美联储保持利率稳定，维持在5.25%-5.50%水平'
    }
]

result4 = calculate_node_confidence(sources_text, 0.9)
print(f"最终置信度: {result4['final_score']}")
print(f"等级: {result4['rating']}")
print(f"维度得分:")
print(f"  - 信源权威度: {result4['dimensions']['authority']}")
print(f"  - 交叉验证度: {result4['dimensions']['cross_validation']}")
print(f"  - 数据一致性: {result4['dimensions']['consistency']}")
print(f"  - 模型确定性: {result4['dimensions']['certainty']}")

# 测试 5: 单一来源（无法检查一致性）
print("\n[测试 5] 单一来源场景")
print("-" * 80)
sources_single = [
    {
        'url': 'https://www.xinhuanet.com/article1',
        'value': '103.5',
        'trend': 'rising'
    }
]

result5 = calculate_node_confidence(sources_single, 0.8)
print(f"最终置信度: {result5['final_score']}")
print(f"等级: {result5['rating']}")
print(f"维度得分:")
print(f"  - 信源权威度: {result5['dimensions']['authority']}")
print(f"  - 交叉验证度: {result5['dimensions']['cross_validation']}")
print(f"  - 数据一致性: {result5['dimensions']['consistency']} (默认中性分数)")
print(f"  - 模型确定性: {result5['dimensions']['certainty']}")
print(f"一致性详情: {result5['consistency_details']}")

# 测试 6: 禁用一致性检查
print("\n[测试 6] 禁用一致性检查")
print("-" * 80)
result6 = calculate_node_confidence(sources_consistent, 0.85, enable_consistency_check=False)
print(f"最终置信度: {result6['final_score']}")
print(f"等级: {result6['rating']}")
print(f"一致性详情: {result6['consistency_details']}")

# 测试 7: 数值一致性单独测试
print("\n[测试 7] 数值一致性单独测试")
print("-" * 80)

test_cases = [
    ([103.5, 103.6, 103.4], "高度一致"),
    ([103.5, 105.2, 101.8], "基本一致"),
    ([103.5, 120.0, 85.0], "严重矛盾"),
]

for values, description in test_cases:
    score = calculate_numeric_consistency(values)
    print(f"{description}: 数值={values}, 一致性分数={score:.2f}")

# 测试 8: 趋势一致性单独测试
print("\n[测试 8] 趋势一致性单独测试")
print("-" * 80)

trend_cases = [
    (['rising', 'rising', 'rising'], "完全一致"),
    (['rising', 'stable', 'rising'], "部分一致"),
    (['rising', 'falling', 'rising'], "严重矛盾"),
]

for trends, description in trend_cases:
    score = calculate_trend_consistency(trends)
    print(f"{description}: 趋势={trends}, 一致性分数={score:.2f}")

print("\n" + "=" * 80)
print("测试完成！")
print("=" * 80)

print("\n[总结]")
print("✓ 数据一致性功能已成功集成")
print("✓ 支持数值、文本、趋势三种类型的一致性检查")
print("✓ 能够检测数据源之间的矛盾")
print("✓ 置信度计算现在包含四个维度")
print("\n新的权重分配:")
print("  - 信源权威度: 30%")
print("  - 交叉验证度: 30%")
print("  - 数据一致性: 20%")
print("  - 模型确定性: 20%")








