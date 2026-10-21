"""
置信度计算工具

用于计算 AI 提取的实体/因果关系的置信度分数
基于四个维度进行加权计算：信源权威度、交叉验证度、数据一致性、模型抽取确定性
"""

from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import logging
import re

logger = logging.getLogger(__name__)


# 域名权威度等级映射
# Tier 1 (1.0): 白名单内的权威网站
# Tier 2 (0.7): 主流新闻媒体、学术机构
# Tier 3 (0.4): 未知来源、博客、论坛等
DOMAIN_TIER_MAP = {
    # Tier 1 - 权威机构和顶级媒体 (1.0)
    'gov.cn': 1.0,
    'edu.cn': 1.0,
    'xinhuanet.com': 1.0,
    'people.com.cn': 1.0,
    'chinanews.com.cn': 1.0,
    'reuters.com': 1.0,
    'bloomberg.com': 1.0,
    'ft.com': 1.0,
    'wsj.com': 1.0,
    'economist.com': 1.0,
    'nature.com': 1.0,
    'science.org': 1.0,
    'arxiv.org': 1.0,
    'who.int': 1.0,
    'worldbank.org': 1.0,
    'imf.org': 1.0,
    
    # Tier 2 - 主流媒体和知名机构 (0.7)
    'caixin.com': 0.7,
    'thepaper.cn': 0.7,
    'yicai.com': 0.7,
    'sina.com.cn': 0.7,
    'sohu.com': 0.7,
    '163.com': 0.7,
    'qq.com': 0.7,
    'cnn.com': 0.7,
    'bbc.com': 0.7,
    'nytimes.com': 0.7,
    'theguardian.com': 0.7,
    'forbes.com': 0.7,
    'cnbc.com': 0.7,
    'techcrunch.com': 0.7,
    'wired.com': 0.7,
    'wikipedia.org': 0.7,
}

# 默认权威度分数（未知来源）
DEFAULT_AUTHORITY_SCORE = 0.4


def extract_domain(url: str) -> str:
    """
    从 URL 中提取域名
    
    Args:
        url: 完整的 URL 地址
        
    Returns:
        提取的域名，如果解析失败则返回空字符串
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ''
        # 移除 www. 前缀
        return hostname.replace('www.', '')
    except Exception as e:
        logger.warning(f"无法解析 URL: {url}, 错误: {str(e)}")
        return ''


def calculate_source_authority(source: Dict[str, Any]) -> float:
    """
    计算单个数据源的权威度分数
    
    Args:
        source: 数据源对象，包含 url 和可选的 domain 字段
        
    Returns:
        权威度分数 (0-1)
    """
    domain = source.get('domain') or extract_domain(source.get('url', ''))
    
    if not domain:
        return DEFAULT_AUTHORITY_SCORE
    
    # 精确匹配
    if domain in DOMAIN_TIER_MAP:
        return DOMAIN_TIER_MAP[domain]
    
    # 模糊匹配（检查是否包含已知域名）
    for known_domain, score in DOMAIN_TIER_MAP.items():
        if known_domain in domain or domain in known_domain:
            return score
    
    # 特殊规则：政府和教育域名
    if domain.endswith(('.gov', '.gov.cn', '.edu', '.edu.cn')):
        return 1.0
    
    return DEFAULT_AUTHORITY_SCORE


def calculate_authority_score(sources: List[Dict[str, Any]]) -> float:
    """
    计算平均信源权威度
    
    公式：authority = Σ(sourceAuthority) / sourceCount
    
    Args:
        sources: 数据源数组
        
    Returns:
        平均权威度分数 (0-1)
    """
    if not sources:
        return DEFAULT_AUTHORITY_SCORE
    
    total_authority = sum(calculate_source_authority(source) for source in sources)
    return total_authority / len(sources)


def calculate_cross_validation_score(sources: List[Dict[str, Any]]) -> float:
    """
    计算交叉验证度分数
    
    使用非线性函数计算，鼓励多来源验证：
    - 1 个来源: 0.4
    - 2 个来源: 0.7
    - 3+ 个来源: 1.0
    
    Args:
        sources: 数据源数组
        
    Returns:
        交叉验证度分数 (0-1)
    """
    if not sources:
        return 0.0
    
    source_count = len(sources)
    
    # 简化的非线性映射
    if source_count == 1:
        return 0.4
    elif source_count == 2:
        return 0.7
    else:
        return 1.0


def determine_rating(score: float) -> str:
    """
    根据最终分数判断置信度等级
    
    - High: > 0.8
    - Medium: 0.5 - 0.8
    - Low: < 0.5
    
    Args:
        score: 最终置信度分数
        
    Returns:
        置信度等级 ('High', 'Medium', 'Low')
    """
    if score > 0.8:
        return 'High'
    elif score >= 0.5:
        return 'Medium'
    else:
        return 'Low'


def extract_numeric_value(text: str) -> Optional[float]:
    """
    从文本中提取数值
    
    支持格式：
    - 整数/小数：123, 123.45
    - 百分比：12.5%
    - 带单位：$100, ¥200, 103.5点
    - 范围：5.25%-5.50% (取中间值)
    
    Args:
        text: 包含数值的文本
        
    Returns:
        提取的数值，如果无法提取则返回 None
    """
    if not text:
        return None
    
    # 移除货币符号和单位
    cleaned = re.sub(r'[¥$€£点]', '', text)
    
    # 处理百分比
    if '%' in cleaned:
        cleaned = cleaned.replace('%', '')
    
    # 处理范围（如 5.25%-5.50%）
    range_match = re.search(r'([\d.]+)\s*[-~至到]\s*([\d.]+)', cleaned)
    if range_match:
        try:
            low = float(range_match.group(1))
            high = float(range_match.group(2))
            return (low + high) / 2
        except ValueError:
            pass
    
    # 提取单个数值
    number_match = re.search(r'-?\d+\.?\d*', cleaned)
    if number_match:
        try:
            return float(number_match.group())
        except ValueError:
            pass
    
    return None


def normalize_text(text: str) -> str:
    """
    标准化文本，用于一致性比较
    
    - 转小写
    - 移除标点符号
    - 移除多余空格
    
    Args:
        text: 原始文本
        
    Returns:
        标准化后的文本
    """
    if not text:
        return ''
    
    # 转小写
    text = text.lower()
    
    # 移除标点符号（保留中文字符）
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
    
    # 移除多余空格
    text = ' '.join(text.split())
    
    return text


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    计算两段文本的相似度（简化版）
    
    使用词汇重叠率作为相似度指标
    
    Args:
        text1: 文本1
        text2: 文本2
        
    Returns:
        相似度分数 (0-1)
    """
    if not text1 or not text2:
        return 0.0
    
    # 标准化文本
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    
    # 分词（简单按空格分割）
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    
    if not words1 or not words2:
        return 0.0
    
    # 计算 Jaccard 相似度
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0


def calculate_consistency_score(sources: List[Dict[str, Any]]) -> float:
    """
    计算数据一致性分数
    
    检查多个来源的数据是否一致：
    1. 如果来源包含数值数据，比较数值的一致性
    2. 如果来源包含文本描述，比较文本的相似度
    3. 如果来源包含趋势判断，检查趋势是否一致
    
    一致性评分标准：
    - 完全一致: 1.0
    - 基本一致: 0.7-0.9
    - 部分矛盾: 0.4-0.6
    - 严重矛盾: 0.0-0.3
    
    Args:
        sources: 数据源数组，每个来源可包含：
                - value: 数值数据
                - description: 文本描述
                - trend: 趋势判断 (rising/falling/stable)
        
    Returns:
        一致性分数 (0-1)
    """
    if not sources or len(sources) < 2:
        # 单一来源无法判断一致性，返回中性分数
        return 0.7
    
    # 提取各来源的数据
    values = []
    descriptions = []
    trends = []
    
    for source in sources:
        # 提取数值
        if 'value' in source and source['value']:
            value_str = str(source['value'])
            numeric_value = extract_numeric_value(value_str)
            if numeric_value is not None:
                values.append(numeric_value)
        
        # 提取描述
        if 'description' in source and source['description']:
            descriptions.append(source['description'])
        
        # 提取趋势
        if 'trend' in source and source['trend']:
            trend = source['trend'].lower()
            if trend in ['rising', 'falling', 'stable', 'up', 'down', 'unchanged']:
                trends.append(trend)
    
    # 计算各类数据的一致性
    scores = []
    
    # 1. 数值一致性
    if len(values) >= 2:
        value_consistency = calculate_numeric_consistency(values)
        scores.append(value_consistency)
    
    # 2. 文本一致性
    if len(descriptions) >= 2:
        text_consistency = calculate_text_consistency(descriptions)
        scores.append(text_consistency)
    
    # 3. 趋势一致性
    if len(trends) >= 2:
        trend_consistency = calculate_trend_consistency(trends)
        scores.append(trend_consistency)
    
    # 如果没有可比较的数据，返回中性分数
    if not scores:
        return 0.7
    
    # 返回平均一致性分数
    return sum(scores) / len(scores)


def calculate_numeric_consistency(values: List[float]) -> float:
    """
    计算数值一致性
    
    使用变异系数（CV）评估数值的离散程度
    CV = 标准差 / 平均值
    
    Args:
        values: 数值列表
        
    Returns:
        一致性分数 (0-1)
    """
    if len(values) < 2:
        return 1.0
    
    # 计算平均值和标准差
    mean = sum(values) / len(values)
    
    if mean == 0:
        # 所有值都是0，完全一致
        return 1.0 if all(v == 0 for v in values) else 0.0
    
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std_dev = variance ** 0.5
    
    # 变异系数
    cv = std_dev / abs(mean)
    
    # 转换为一致性分数
    # CV < 0.05: 高度一致 (1.0)
    # CV < 0.15: 基本一致 (0.8)
    # CV < 0.30: 部分一致 (0.6)
    # CV >= 0.30: 不一致 (0.3)
    if cv < 0.05:
        return 1.0
    elif cv < 0.15:
        return 0.8
    elif cv < 0.30:
        return 0.6
    else:
        return max(0.3, 1.0 - cv)


def calculate_text_consistency(descriptions: List[str]) -> float:
    """
    计算文本描述一致性
    
    比较所有文本对的相似度，取平均值
    
    Args:
        descriptions: 文本描述列表
        
    Returns:
        一致性分数 (0-1)
    """
    if len(descriptions) < 2:
        return 1.0
    
    similarities = []
    
    # 两两比较
    for i in range(len(descriptions)):
        for j in range(i + 1, len(descriptions)):
            similarity = calculate_text_similarity(descriptions[i], descriptions[j])
            similarities.append(similarity)
    
    if not similarities:
        return 0.7
    
    # 返回平均相似度
    avg_similarity = sum(similarities) / len(similarities)
    
    # 相似度阈值调整
    # > 0.7: 高度一致
    # 0.4-0.7: 基本一致
    # < 0.4: 不一致
    if avg_similarity > 0.7:
        return 1.0
    elif avg_similarity > 0.4:
        return 0.7 + (avg_similarity - 0.4) * 0.3 / 0.3
    else:
        return 0.4 + avg_similarity


def calculate_trend_consistency(trends: List[str]) -> float:
    """
    计算趋势判断一致性
    
    检查趋势判断是否一致
    
    Args:
        trends: 趋势列表 (rising/falling/stable等)
        
    Returns:
        一致性分数 (0-1)
    """
    if len(trends) < 2:
        return 1.0
    
    # 标准化趋势
    normalized_trends = []
    for trend in trends:
        trend_lower = trend.lower()
        if trend_lower in ['rising', 'up', 'increase', '上涨', '上升']:
            normalized_trends.append('rising')
        elif trend_lower in ['falling', 'down', 'decrease', '下跌', '下降']:
            normalized_trends.append('falling')
        elif trend_lower in ['stable', 'unchanged', 'flat', '稳定', '不变']:
            normalized_trends.append('stable')
        else:
            normalized_trends.append(trend_lower)
    
    # 计算一致性
    unique_trends = set(normalized_trends)
    
    if len(unique_trends) == 1:
        # 完全一致
        return 1.0
    elif len(unique_trends) == 2:
        # 部分一致（可能有一个异常值）
        # 检查是否有矛盾趋势（rising vs falling）
        if ('rising' in unique_trends and 'falling' in unique_trends):
            return 0.3  # 严重矛盾
        else:
            return 0.6  # 部分不一致
    else:
        # 多种趋势，不一致
        return 0.4


def calculate_node_confidence(
    sources: List[Dict[str, Any]],
    llm_score: float,
    enable_consistency_check: bool = True
) -> Dict[str, Any]:
    """
    计算节点置信度分数
    
    基于四个维度进行加权计算：
    1. Authority (信源权威度): 权重 0.3
    2. Cross Validation (交叉验证度): 权重 0.3
    3. Consistency (数据一致性): 权重 0.2
    4. LLM Certainty (模型抽取确定性): 权重 0.2
    
    最终公式：
    finalScore = authority * 0.3 + crossValidation * 0.3 + consistency * 0.2 + llmScore * 0.2
    
    Args:
        sources: 数据源数组，用于计算权威度、交叉验证度和一致性
                每个来源可包含：
                - url: 数据源URL（必需）
                - domain: 域名（可选）
                - value: 数值数据（可选）
                - description: 文本描述（可选）
                - trend: 趋势判断（可选）
        llm_score: LLM 模型的确定性分数 (0.1-1.0)
        enable_consistency_check: 是否启用一致性检查（默认True）
        
    Returns:
        置信度计算结果字典，包含：
        - final_score: 最终置信度分数 (保留两位小数)
        - dimensions: 各维度得分详情
        - rating: 置信度等级 ('High', 'Medium', 'Low')
        - consistency_details: 一致性检查详情（如果启用）
        
    Example:
        >>> sources = [
        ...     {
        ...         'url': 'https://www.xinhuanet.com/article1',
        ...         'value': '103.5',
        ...         'trend': 'rising'
        ...     },
        ...     {
        ...         'url': 'https://www.reuters.com/article2',
        ...         'value': '103.8',
        ...         'trend': 'rising'
        ...     },
        ...     {
        ...         'url': 'https://www.bloomberg.com/article3',
        ...         'value': '103.6',
        ...         'trend': 'rising'
        ...     }
        ... ]
        >>> result = calculate_node_confidence(sources, 0.85)
        >>> print(result)
        {
            'final_score': 0.91,
            'dimensions': {
                'authority': 1.0,
                'cross_validation': 1.0,
                'consistency': 0.95,
                'certainty': 0.85
            },
            'rating': 'High',
            'consistency_details': {
                'numeric_consistency': 0.95,
                'has_conflicts': False
            }
        }
    """
    # 参数验证
    valid_llm_score = max(0.1, min(1.0, llm_score))
    valid_sources = sources or []
    
    # 计算各维度得分
    authority = calculate_authority_score(valid_sources)
    cross_validation = calculate_cross_validation_score(valid_sources)
    certainty = valid_llm_score
    
    # 计算一致性分数
    consistency = 0.7  # 默认中性分数
    consistency_details = {}
    
    if enable_consistency_check and len(valid_sources) >= 2:
        consistency = calculate_consistency_score(valid_sources)
        consistency_details = {
            'enabled': True,
            'source_count': len(valid_sources),
            'has_conflicts': consistency < 0.5
        }
    else:
        consistency_details = {
            'enabled': False,
            'reason': 'Not enough sources' if len(valid_sources) < 2 else 'Disabled'
        }
    
    # 加权计算最终分数
    WEIGHT_AUTHORITY = 0.3
    WEIGHT_CROSS_VALIDATION = 0.3
    WEIGHT_CONSISTENCY = 0.2
    WEIGHT_CERTAINTY = 0.2
    
    raw_score = (
        authority * WEIGHT_AUTHORITY +
        cross_validation * WEIGHT_CROSS_VALIDATION +
        consistency * WEIGHT_CONSISTENCY +
        certainty * WEIGHT_CERTAINTY
    )
    
    # 保留两位小数
    final_score = round(raw_score, 2)
    
    # 判断等级
    rating = determine_rating(final_score)
    
    result = {
        'final_score': final_score,
        'dimensions': {
            'authority': round(authority, 2),
            'cross_validation': round(cross_validation, 2),
            'consistency': round(consistency, 2),
            'certainty': round(certainty, 2)
        },
        'rating': rating,
        'consistency_details': consistency_details
    }
    
    # 如果检测到严重冲突，添加警告
    if consistency < 0.5:
        result['warning'] = '检测到数据源之间存在严重冲突，请谨慎使用'
    
    return result


def calculate_batch_confidence(
    nodes: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    批量计算多个节点的置信度
    
    Args:
        nodes: 节点数组，每个节点包含 sources 和 llm_score
        
    Returns:
        置信度结果数组
    """
    results = []
    for node in nodes:
        sources = node.get('sources', [])
        llm_score = node.get('llm_score', 0.5)
        result = calculate_node_confidence(sources, llm_score)
        results.append(result)
    return results


def get_confidence_label(rating: str) -> str:
    """
    获取置信度等级的中文标签
    
    Args:
        rating: 置信度等级 ('High', 'Medium', 'Low')
        
    Returns:
        中文标签
    """
    labels = {
        'High': '高置信度',
        'Medium': '中等置信度',
        'Low': '低置信度'
    }
    return labels.get(rating, '未知')


def get_confidence_color(rating: str) -> str:
    """
    获取置信度等级对应的颜色
    
    Args:
        rating: 置信度等级 ('High', 'Medium', 'Low')
        
    Returns:
        颜色值（十六进制）
    """
    colors = {
        'High': '#10b981',    # green-500
        'Medium': '#f59e0b',  # amber-500
        'Low': '#ef4444'      # red-500
    }
    return colors.get(rating, '#6b7280')  # gray-500





