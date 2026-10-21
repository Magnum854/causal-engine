/**
 * NodeDetailDrawer 测试数据
 * 提供多种场景的示例数据
 */

// 示例 1: 完整数据 - 美联储加息
export const fedRateHikeData = {
  meta: {
    title: "美联储加息预期",
    category: "货币政策",
    risk_level: "high",
    current_metric: {
      label: "联邦基金利率",
      value: "5.25%",
      trend: "up"
    }
  },
  topology: {
    causes: ["通胀压力", "就业市场强劲", "工资增长"],
    effects: ["美元走强", "股市波动", "债券收益率上升", "房地产降温"]
  },
  temporal_dynamics: {
    past: {
      summary: "2022年3月开始，美联储启动了40年来最激进的加息周期，累计加息525个基点，以应对高达9.1%的通胀率。历史上看，如此快速的加息往往伴随经济衰退风险。"
    },
    present: {
      summary: "当前联邦基金利率维持在5.25%-5.50%区间，通胀已回落至3.2%，但仍高于2%目标。劳动力市场依然紧张，失业率保持在3.7%低位。市场预期美联储将在2024年开始降息。"
    },
    future: {
      base_case: {
        title: "基准情景：软着陆",
        probability: "65%",
        description: "美联储成功控制通胀，经济实现软着陆。预计2024年下半年开始降息，全年降息75-100个基点。消费和投资保持韧性。",
        key_metrics: [
          { label: "2024年底利率", value: "4.50%" },
          { label: "GDP增长", value: "1.8%" },
          { label: "失业率", value: "4.2%" },
          { label: "核心PCE通胀", value: "2.3%" }
        ]
      },
      tail_risk: {
        title: "尾部风险：经济衰退",
        probability: "25%",
        description: "持续高利率导致经济硬着陆，失业率飙升，美联储被迫紧急降息。信贷市场出现系统性风险，企业违约率上升。",
        key_metrics: [
          { label: "2024年底利率", value: "3.00%" },
          { label: "GDP增长", value: "-0.5%" },
          { label: "失业率", value: "5.8%" },
          { label: "企业违约率", value: "4.2%" }
        ]
      }
    }
  },
  evidence: {
    confidence_score: 0.85,
    sources: [
      {
        title: "美联储12月FOMC会议纪要：暗示2024年可能降息三次",
        url: "https://www.federalreserve.gov/newsevents/pressreleases.htm",
        date: "2024-01-03"
      },
      {
        title: "鲍威尔：通胀已显著回落，但仍需保持警惕",
        url: "https://www.federalreserve.gov/newsevents/speech/powell20240110a.htm",
        date: "2024-01-10"
      },
      {
        title: "华尔街日报：市场押注美联储3月开始降息",
        url: "https://www.wsj.com/economy/central-banking/fed-rate-cuts-2024",
        date: "2024-01-15"
      },
      {
        title: "高盛：预计2024年美联储将降息125个基点",
        url: "https://www.goldmansachs.com/insights/pages/fed-outlook-2024.html",
        date: "2024-01-18"
      },
      {
        title: "美国12月CPI同比上涨3.4%，超出预期",
        url: "https://www.bls.gov/news.release/cpi.nr0.htm",
        date: "2024-01-11"
      }
    ]
  }
}

// 示例 2: 中等风险 - 中国房地产
export const chinaRealEstateData = {
  meta: {
    title: "中国房地产市场调整",
    category: "房地产",
    risk_level: "medium",
    current_metric: {
      label: "70城房价指数",
      value: "-0.3%",
      trend: "down"
    }
  },
  topology: {
    causes: ["人口老龄化", "政策调控", "居民杠杆率高"],
    effects: ["地方财政压力", "银行资产质量", "消费信心"]
  },
  temporal_dynamics: {
    past: {
      summary: "2021年"三道红线"政策出台后，房地产行业进入深度调整期。恒大、碧桂园等头部房企陷入债务危机，行业销售额连续两年下滑超过20%。"
    },
    present: {
      summary: "2024年初，政策端持续发力，多地放松限购限贷。但需求端复苏缓慢，一线城市成交量环比改善，但二三线城市库存压力依然较大。"
    },
    future: {
      base_case: {
        title: "基准情景：缓慢筑底",
        probability: "60%",
        description: "政策支持下，市场逐步企稳，但难以回到高增长时代。行业集中度提升，优质房企受益。",
        key_metrics: [
          { label: "2024年销售额", value: "-5%" },
          { label: "新开工面积", value: "-8%" },
          { label: "房价涨幅", value: "0-2%" }
        ]
      },
      tail_risk: {
        title: "尾部风险：系统性风险",
        probability: "15%",
        description: "更多房企违约，引发金融系统风险。地方政府土地出让收入大幅下滑，财政危机蔓延。",
        key_metrics: [
          { label: "房企违约率", value: "15%" },
          { label: "土地出让收入", value: "-30%" },
          { label: "银行不良率", value: "3.5%" }
        ]
      }
    }
  },
  evidence: {
    confidence_score: 0.78,
    sources: [
      {
        title: "国家统计局：1月70城房价环比下降0.3%",
        url: "https://www.stats.gov.cn/",
        date: "2024-02-15"
      },
      {
        title: "央行：将继续支持房地产市场平稳健康发展",
        url: "https://www.pbc.gov.cn/",
        date: "2024-02-10"
      },
      {
        title: "碧桂园：2023年销售额同比下降超40%",
        url: "https://www.countrygarden.com.cn/",
        date: "2024-01-30"
      }
    ]
  }
}

// 示例 3: 低风险 - AI 技术发展
export const aiTechData = {
  meta: {
    title: "生成式AI技术突破",
    category: "科技创新",
    risk_level: "low",
    current_metric: {
      label: "全球AI投资",
      value: "$1,200亿",
      trend: "up"
    }
  },
  topology: {
    causes: ["算力提升", "大模型突破", "数据积累"],
    effects: ["生产力革命", "就业结构变化", "新商业模式"]
  },
  temporal_dynamics: {
    past: {
      summary: "2022年底ChatGPT发布，标志着生成式AI进入大众视野。2023年成为AI元年，各大科技巨头纷纷推出大模型产品，应用场景快速拓展。"
    },
    present: {
      summary: "2024年，AI技术从"玩具"走向"工具"。企业级应用加速落地，AI助手、代码生成、内容创作等场景渗透率快速提升。监管框架逐步建立。"
    },
    future: {
      base_case: {
        title: "基准情景：持续渗透",
        probability: "75%",
        description: "AI技术在各行业深度渗透，成为新的基础设施。生产力大幅提升，但也带来就业结构调整压力。",
        key_metrics: [
          { label: "2025年市场规模", value: "$2,500亿" },
          { label: "企业采用率", value: "65%" },
          { label: "生产力提升", value: "15-20%" }
        ]
      },
      tail_risk: {
        title: "尾部风险：技术泡沫",
        probability: "20%",
        description: "AI应用落地不及预期，投资回报率低于预期。部分AI公司估值大幅回调，行业进入调整期。",
        key_metrics: [
          { label: "AI公司估值", value: "-40%" },
          { label: "投资额", value: "-50%" },
          { label: "失业率上升", value: "1.5%" }
        ]
      }
    }
  },
  evidence: {
    confidence_score: 0.92,
    sources: [
      {
        title: "OpenAI发布GPT-5，多模态能力大幅提升",
        url: "https://openai.com/blog/gpt-5",
        date: "2024-02-20"
      },
      {
        title: "麦肯锡：AI将在2030年前创造13万亿美元经济价值",
        url: "https://www.mckinsey.com/ai-impact-2024",
        date: "2024-02-15"
      },
      {
        title: "微软：Copilot用户数突破1亿",
        url: "https://www.microsoft.com/copilot-milestone",
        date: "2024-02-10"
      },
      {
        title: "欧盟通过AI法案，全球首个AI监管框架落地",
        url: "https://ec.europa.eu/ai-act",
        date: "2024-02-05"
      }
    ]
  }
}

// 示例 4: 最小化数据
export const minimalData = {
  meta: {
    title: "简单节点示例"
  }
}

// 示例 5: 只有元信息和拓扑
export const topologyOnlyData = {
  meta: {
    title: "供应链中断",
    category: "供应链",
    risk_level: "high"
  },
  topology: {
    causes: ["地缘冲突", "极端天气", "港口拥堵"],
    effects: ["物价上涨", "企业成本增加", "消费者信心下降"]
  }
}

// 示例 6: 只有时间动态
export const temporalOnlyData = {
  meta: {
    title: "全球气候变化",
    category: "环境",
    risk_level: "high",
    current_metric: {
      label: "全球平均气温",
      value: "+1.2°C",
      trend: "up"
    }
  },
  temporal_dynamics: {
    past: {
      summary: "工业革命以来，全球平均气温上升约1.2°C。极端天气事件频率显著增加，冰川融化加速。"
    },
    present: {
      summary: "2023年成为有记录以来最热的一年。各国加速碳中和进程，但减排目标与实际行动仍有差距。"
    },
    future: {
      base_case: {
        title: "基准情景：2°C路径",
        probability: "55%",
        description: "各国履行巴黎协定承诺，全球升温控制在2°C以内。但仍需面对海平面上升、极端天气等挑战。",
        key_metrics: [
          { label: "2050年升温", value: "+1.8°C" },
          { label: "可再生能源占比", value: "70%" },
          { label: "碳排放", value: "-60%" }
        ]
      },
      tail_risk: {
        title: "尾部风险：3°C+灾难",
        probability: "30%",
        description: "减排行动不力，全球升温超过3°C。大规模生态系统崩溃，数亿人口面临生存威胁。",
        key_metrics: [
          { label: "2050年升温", value: "+3.2°C" },
          { label: "海平面上升", value: "1.5米" },
          { label: "气候难民", value: "2亿人" }
        ]
      }
    }
  },
  evidence: {
    confidence_score: 0.95,
    sources: [
      {
        title: "IPCC第六次评估报告：气候变化加速",
        url: "https://www.ipcc.ch/report/ar6/",
        date: "2023-03-20"
      },
      {
        title: "WMO：2023年全球平均气温创历史新高",
        url: "https://public.wmo.int/en",
        date: "2024-01-12"
      }
    ]
  }
}

// 导出所有测试数据
export const testDataCollection = {
  fedRateHike: fedRateHikeData,
  chinaRealEstate: chinaRealEstateData,
  aiTech: aiTechData,
  minimal: minimalData,
  topologyOnly: topologyOnlyData,
  temporalOnly: temporalOnlyData
}

export default testDataCollection












