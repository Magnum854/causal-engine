/**
 * 使用示例和测试页面
 * 展示如何使用 CausalGraphViewer 组件
 */

import { useState } from 'react'
import CausalGraphViewer from './components/CausalGraphViewer'

// 模拟的后端数据
const mockAnalysisResult = {
  nodes: [
    {
      id: 'n1',
      label: '全球供应链中断',
      type: 'cause',
      description: '疫情和地缘政治导致的全球供应链问题',
      confidence: 0.95
    },
    {
      id: 'n2',
      label: '能源价格飙升',
      type: 'cause',
      description: '国际能源市场价格大幅上涨',
      confidence: 0.95
    },
    {
      id: 'n3',
      label: '通货膨胀',
      type: 'intermediate',
      description: '物价水平持续上涨',
      confidence: 0.9
    },
    {
      id: 'n4',
      label: '央行提高利率',
      type: 'intermediate',
      description: '货币政策收紧',
      confidence: 0.9
    },
    {
      id: 'n5',
      label: '企业融资成本上升',
      type: 'intermediate',
      description: '借贷成本增加',
      confidence: 0.85
    },
    {
      id: 'n6',
      label: '消费者信心下降',
      type: 'intermediate',
      description: '消费意愿减弱',
      confidence: 0.8
    },
    {
      id: 'n7',
      label: '经济衰退风险',
      type: 'effect',
      description: '经济增长放缓或负增长',
      confidence: 0.75
    }
  ],
  edges: [
    {
      source: 'n1',
      target: 'n3',
      label: '直接导致',
      description: '供应链中断推高商品价格',
      strength: 0.9
    },
    {
      source: 'n2',
      target: 'n3',
      label: '直接导致',
      description: '能源价格上涨推高整体物价',
      strength: 0.9
    },
    {
      source: 'n3',
      target: 'n4',
      label: '迫使',
      description: '通胀压力迫使央行加息',
      strength: 0.85
    },
    {
      source: 'n4',
      target: 'n5',
      label: '直接导致',
      description: '利率上升增加借贷成本',
      strength: 0.95
    },
    {
      source: 'n3',
      target: 'n6',
      label: '影响',
      description: '物价上涨降低消费意愿',
      strength: 0.8
    },
    {
      source: 'n5',
      target: 'n7',
      label: '可能引发',
      description: '融资困难影响企业运营',
      strength: 0.75
    },
    {
      source: 'n6',
      target: 'n7',
      label: '可能引发',
      description: '消费疲软拖累经济增长',
      strength: 0.7
    }
  ],
  explanation: '这是一条典型的经济因果链：全球供应链中断和能源价格飙升共同推高了通货膨胀，迫使央行采取加息政策。高利率虽然能抑制通胀，但也导致企业融资成本上升和消费者信心下降，最终可能引发经济衰退。'
}

function ExamplePage() {
  const [analysisResult, setAnalysisResult] = useState(mockAnalysisResult)
  const [layoutDirection, setLayoutDirection] = useState('LR')

  const handleNodeClick = (node) => {
    console.log('节点被点击:', node)
  }

  const handleLoadNewData = () => {
    // 模拟加载新数据
    console.log('加载新数据...')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* 头部 */}
      <header className="border-b border-white/10 backdrop-blur-sm bg-white/5">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400">
                因果图谱可视化
              </h1>
              <p className="text-slate-300 mt-2 text-sm">
                交互式因果关系图谱展示
              </p>
            </div>
            
            {/* 布局方向切换 */}
            <div className="flex items-center gap-4">
              <label className="text-slate-300 text-sm">布局方向:</label>
              <select
                value={layoutDirection}
                onChange={(e) => setLayoutDirection(e.target.value)}
                className="bg-slate-800 text-white px-3 py-2 rounded-lg border border-slate-700"
              >
                <option value="LR">从左到右</option>
                <option value="TB">从上到下</option>
                <option value="RL">从右到左</option>
                <option value="BT">从下到上</option>
              </select>
            </div>
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <div className="container mx-auto px-6 py-8">
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-white/10 shadow-2xl overflow-hidden">
          {/* 说明文字 */}
          <div className="p-6 border-b border-white/10">
            <h2 className="text-xl font-semibold text-white mb-2">
              因果关系图谱
            </h2>
            <p className="text-slate-400 text-sm">
              点击节点查看详细信息 • 拖拽移动视图 • 滚轮缩放
            </p>
          </div>

          {/* 图谱容器 */}
          <div className="h-[700px]">
            <CausalGraphViewer
              analysisResult={analysisResult}
              onNodeClick={handleNodeClick}
              layoutDirection={layoutDirection}
            />
          </div>
        </div>

        {/* 分析说明 */}
        {analysisResult?.explanation && (
          <div className="mt-6 bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-white/10 shadow-2xl p-6">
            <h3 className="text-lg font-semibold text-white mb-3">
              分析说明
            </h3>
            <p className="text-slate-300 leading-relaxed">
              {analysisResult.explanation}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default ExamplePage








