/**
 * 置信度计算工具
 * 
 * 用于计算 AI 提取的实体/因果关系的置信度分数
 * 基于三个维度进行加权计算：信源权威度、交叉验证度、模型抽取确定性
 */

/**
 * 数据源信息接口
 */
export interface DataSource {
  /** 数据源 URL */
  url: string
  /** 数据源域名 */
  domain?: string
  /** 数据源标题 */
  title?: string
}

/**
 * 置信度计算结果接口
 */
export interface ConfidenceResult {
  /** 最终置信度分数 (0-1, 保留两位小数) */
  finalScore: number
  /** 各维度得分详情 */
  dimensions: {
    /** 信源权威度得分 (0-1) */
    authority: number
    /** 交叉验证度得分 (0-1) */
    crossValidation: number
    /** 模型抽取确定性得分 (0-1) */
    certainty: number
  }
  /** 置信度等级 */
  rating: 'High' | 'Medium' | 'Low'
}

/**
 * 域名权威度等级映射
 * 
 * Tier 1 (1.0): 白名单内的权威网站
 * Tier 2 (0.7): 主流新闻媒体、学术机构
 * Tier 3 (0.4): 未知来源、博客、论坛等
 */
const DOMAIN_TIER_MAP: Record<string, number> = {
  // Tier 1 - 权威机构和顶级媒体 (1.0)
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
  
  // Tier 2 - 主流媒体和知名机构 (0.7)
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

/**
 * 默认权威度分数（未知来源）
 */
const DEFAULT_AUTHORITY_SCORE = 0.4

/**
 * 从 URL 中提取域名
 * 
 * @param url - 完整的 URL 地址
 * @returns 提取的域名，如果解析失败则返回空字符串
 */
function extractDomain(url: string): string {
  try {
    const urlObj = new URL(url)
    return urlObj.hostname.replace(/^www\./, '')
  } catch {
    return ''
  }
}

/**
 * 计算单个数据源的权威度分数
 * 
 * @param source - 数据源对象
 * @returns 权威度分数 (0-1)
 */
function calculateSourceAuthority(source: DataSource): number {
  const domain = source.domain || extractDomain(source.url)
  
  if (!domain) {
    return DEFAULT_AUTHORITY_SCORE
  }
  
  // 精确匹配
  if (domain in DOMAIN_TIER_MAP) {
    return DOMAIN_TIER_MAP[domain]
  }
  
  // 模糊匹配（检查是否包含已知域名）
  for (const [knownDomain, score] of Object.entries(DOMAIN_TIER_MAP)) {
    if (domain.includes(knownDomain) || knownDomain.includes(domain)) {
      return score
    }
  }
  
  // 特殊规则：政府和教育域名
  if (domain.endsWith('.gov') || domain.endsWith('.gov.cn') || 
      domain.endsWith('.edu') || domain.endsWith('.edu.cn')) {
    return 1.0
  }
  
  return DEFAULT_AUTHORITY_SCORE
}

/**
 * 计算平均信源权威度
 * 
 * 公式：authority = Σ(sourceAuthority) / sourceCount
 * 
 * @param sources - 数据源数组
 * @returns 平均权威度分数 (0-1)
 */
function calculateAuthorityScore(sources: DataSource[]): number {
  if (!sources || sources.length === 0) {
    return DEFAULT_AUTHORITY_SCORE
  }
  
  const totalAuthority = sources.reduce((sum, source) => {
    return sum + calculateSourceAuthority(source)
  }, 0)
  
  return totalAuthority / sources.length
}

/**
 * 计算交叉验证度分数
 * 
 * 使用非线性函数计算，鼓励多来源验证：
 * - 1 个来源: 0.4
 * - 2 个来源: 0.7
 * - 3+ 个来源: 1.0
 * 
 * 公式：crossValidation = min(1.0, 0.4 + 0.3 * log2(sourceCount))
 * 
 * @param sources - 数据源数组
 * @returns 交叉验证度分数 (0-1)
 */
function calculateCrossValidationScore(sources: DataSource[]): number {
  if (!sources || sources.length === 0) {
    return 0.0
  }
  
  const sourceCount = sources.length
  
  // 简化的非线性映射
  if (sourceCount === 1) {
    return 0.4
  } else if (sourceCount === 2) {
    return 0.7
  } else {
    return 1.0
  }
  
  // 或者使用更平滑的对数函数（可选）
  // return Math.min(1.0, 0.4 + 0.3 * Math.log2(sourceCount))
}

/**
 * 根据最终分数判断置信度等级
 * 
 * - High: > 0.8
 * - Medium: 0.5 - 0.8
 * - Low: < 0.5
 * 
 * @param score - 最终置信度分数
 * @returns 置信度等级
 */
function determineRating(score: number): 'High' | 'Medium' | 'Low' {
  if (score > 0.8) {
    return 'High'
  } else if (score >= 0.5) {
    return 'Medium'
  } else {
    return 'Low'
  }
}

/**
 * 计算节点置信度分数
 * 
 * 基于三个维度进行加权计算：
 * 1. Authority (信源权威度): 权重 0.4
 * 2. Cross Validation (交叉验证度): 权重 0.4
 * 3. LLM Certainty (模型抽取确定性): 权重 0.2
 * 
 * 最终公式：
 * finalScore = authority * 0.4 + crossValidation * 0.4 + llmScore * 0.2
 * 
 * @param sources - 数据源数组，用于计算权威度和交叉验证度
 * @param llmScore - LLM 模型的确定性分数 (0.1-1.0)
 * @returns 置信度计算结果对象
 * 
 * @example
 * ```typescript
 * const sources = [
 *   { url: 'https://www.xinhuanet.com/article1' },
 *   { url: 'https://www.reuters.com/article2' },
 *   { url: 'https://www.bloomberg.com/article3' }
 * ]
 * 
 * const result = calculateNodeConfidence(sources, 0.85)
 * console.log(result)
 * // {
 * //   finalScore: 0.89,
 * //   dimensions: {
 * //     authority: 1.0,
 * //     crossValidation: 1.0,
 * //     certainty: 0.85
 * //   },
 * //   rating: 'High'
 * // }
 * ```
 */
export function calculateNodeConfidence(
  sources: DataSource[],
  llmScore: number
): ConfidenceResult {
  // 参数验证
  const validLlmScore = Math.max(0.1, Math.min(1.0, llmScore))
  const validSources = sources || []
  
  // 计算各维度得分
  const authority = calculateAuthorityScore(validSources)
  const crossValidation = calculateCrossValidationScore(validSources)
  const certainty = validLlmScore
  
  // 加权计算最终分数
  const WEIGHT_AUTHORITY = 0.4
  const WEIGHT_CROSS_VALIDATION = 0.4
  const WEIGHT_CERTAINTY = 0.2
  
  const rawScore = 
    authority * WEIGHT_AUTHORITY +
    crossValidation * WEIGHT_CROSS_VALIDATION +
    certainty * WEIGHT_CERTAINTY
  
  // 保留两位小数
  const finalScore = Math.round(rawScore * 100) / 100
  
  // 判断等级
  const rating = determineRating(finalScore)
  
  return {
    finalScore,
    dimensions: {
      authority: Math.round(authority * 100) / 100,
      crossValidation: Math.round(crossValidation * 100) / 100,
      certainty: Math.round(certainty * 100) / 100,
    },
    rating,
  }
}

/**
 * 批量计算多个节点的置信度
 * 
 * @param nodes - 节点数组，每个节点包含 sources 和 llmScore
 * @returns 置信度结果数组
 */
export function calculateBatchConfidence(
  nodes: Array<{ sources: DataSource[]; llmScore: number }>
): ConfidenceResult[] {
  return nodes.map(node => calculateNodeConfidence(node.sources, node.llmScore))
}

/**
 * 获取置信度等级的中文标签
 * 
 * @param rating - 置信度等级
 * @returns 中文标签
 */
export function getConfidenceLabel(rating: 'High' | 'Medium' | 'Low'): string {
  const labels = {
    High: '高置信度',
    Medium: '中等置信度',
    Low: '低置信度',
  }
  return labels[rating]
}

/**
 * 获取置信度等级对应的颜色
 * 
 * @param rating - 置信度等级
 * @returns 颜色值（Tailwind CSS 类名或十六进制）
 */
export function getConfidenceColor(rating: 'High' | 'Medium' | 'Low'): string {
  const colors = {
    High: '#10b981', // green-500
    Medium: '#f59e0b', // amber-500
    Low: '#ef4444', // red-500
  }
  return colors[rating]
}












