/**
 * NodeDetailDrawer 使用示例
 * 展示如何集成节点详情抽屉组件
 */

import { useState } from 'react'
import NodeDetailDrawer from './NodeDetailDrawer'

// 示例数据
const exampleNodeData = {
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
    causes: ["通胀压力", "就业市场强劲"],
    effects: ["美元走强", "股市波动", "债券收益率上升"]
  },
  temporal_dynamics: {
    past: {
      summary: "2022年3月开始，美联储启动了40年来最激进的加息周期，累计加息525个基点，以应对高达9.1%的通胀率。"
    },
    present: {
      summary: "当前联邦基金利率维持在5.25%-5.50%区间，通胀已回落至3.2%，但仍高于2%目标。市场预期美联储将在2024年开始降息。"
    },
    future: {
      base_case: {
        title: "基准情景：软着陆",
        probability: "65%",
        description: "美联储成功控制通胀，经济实现软着陆。预计2024年下半年开始降息，全年降息75-100个基点。",
        key_metrics: [
          { label: "2024年底利率", value: "4.50%" },
          { label: "GDP增长", value: "1.8%" },
          { label: "失业率", value: "4.2%" }
        ]
      },
      tail_risk: {
        title: "尾部风险：经济衰退",
        probability: "25%",
        description: "持续高利率导致经济硬着陆，失业率飙升，美联储被迫紧急降息。信贷市场出现系统性风险。",
        key_metrics: [
          { label: "2024年底利率", value: "3.00%" },
          { label: "GDP增长", value: "-0.5%" },
          { label: "失业率", value: "5.8%" }
        ]
      }
    }
  },
  evidence: {
    confidence_score: 0.85,
    sources: [
      {
        title: "美联储12月FOMC会议纪要：暗示2024年可能降息三次",
        url: "https://example.com/fed-minutes",
        date: "2024-01-03"
      },
      {
        title: "鲍威尔：通胀已显著回落，但仍需保持警惕",
        url: "https://example.com/powell-speech",
        date: "2024-01-10"
      },
      {
        title: "华尔街日报：市场押注美联储3月开始降息",
        url: "https://example.com/wsj-analysis",
        date: "2024-01-15"
      },
      {
        title: "高盛：预计2024年美联储将降息125个基点",
        url: "https://example.com/goldman-forecast",
        date: "2024-01-18"
      },
      {
        title: "美国12月CPI同比上涨3.4%，超出预期",
        url: "https://example.com/cpi-data",
        date: "2024-01-11"
      }
    ]
  }
}

/**
 * 使用示例组件
 */
function NodeDetailDrawerExample() {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)

  return (
    <div className="min-h-screen bg-slate-900 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">
          NodeDetailDrawer 组件示例
        </h1>

        {/* 触发按钮 */}
        <button
          onClick={() => setIsDrawerOpen(true)}
          className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg shadow-lg transition-colors"
        >
          打开节点详情抽屉
        </button>

        {/* 说明文档 */}
        <div className="mt-8 bg-slate-800 rounded-lg p-6 text-slate-300">
          <h2 className="text-xl font-bold text-white mb-4">使用说明</h2>
          
          <div className="space-y-4 text-sm">
            <div>
              <h3 className="font-semibold text-white mb-2">基本用法：</h3>
              <pre className="bg-slate-900 p-4 rounded overflow-x-auto">
{`import NodeDetailDrawer from './components/NodeDetailDrawer'

function MyComponent() {
  const [isOpen, setIsOpen] = useState(false)
  const [nodeData, setNodeData] = useState(null)

  return (
    <>
      <button onClick={() => setIsOpen(true)}>
        查看详情
      </button>
      
      <NodeDetailDrawer
        nodeData={nodeData}
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
      />
    </>
  )
}`}
              </pre>
            </div>

            <div>
              <h3 className="font-semibold text-white mb-2">Props 说明：</h3>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li><code className="text-purple-400">nodeData</code>: 节点数据对象（必需）</li>
                <li><code className="text-purple-400">isOpen</code>: 控制抽屉显示/隐藏（必需）</li>
                <li><code className="text-purple-400">onClose</code>: 关闭抽屉的回调函数（必需）</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold text-white mb-2">数据结构：</h3>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li><code className="text-purple-400">meta</code>: 元信息（标题、分类、风险等级、当前指标）</li>
                <li><code className="text-purple-400">topology</code>: 因果拓扑（原因、结果节点）</li>
                <li><code className="text-purple-400">temporal_dynamics</code>: 时空动态（过去、现在、未来）</li>
                <li><code className="text-purple-400">evidence</code>: 证据信源（置信度、新闻来源）</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* NodeDetailDrawer 组件 */}
      <NodeDetailDrawer
        nodeData={exampleNodeData}
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
      />
    </div>
  )
}

export default NodeDetailDrawerExample












