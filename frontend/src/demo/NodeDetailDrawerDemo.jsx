/**
 * NodeDetailDrawer 完整演示页面
 * 展示所有测试场景和交互效果
 */

import { useState } from 'react'
import NodeDetailDrawer from './components/NodeDetailDrawer'
import testDataCollection from './components/NodeDetailDrawer.testData'
import { TrendingUp, Home, Building2, Cpu, Minimize2, Network, Globe } from 'lucide-react'

function NodeDetailDrawerDemo() {
  const [selectedData, setSelectedData] = useState(null)
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)

  const handleCardClick = (data) => {
    setSelectedData(data)
    setIsDrawerOpen(true)
  }

  const handleCloseDrawer = () => {
    setIsDrawerOpen(false)
    // 延迟清空数据，等待动画完成
    setTimeout(() => setSelectedData(null), 300)
  }

  // 场景卡片配置
  const scenarios = [
    {
      id: 'fedRateHike',
      title: '美联储加息预期',
      description: '完整数据示例 - 包含所有区块',
      icon: <TrendingUp className="w-6 h-6" />,
      color: 'from-red-500 to-orange-500',
      data: testDataCollection.fedRateHike
    },
    {
      id: 'chinaRealEstate',
      title: '中国房地产市场',
      description: '中等风险场景 - 房地产调整',
      icon: <Building2 className="w-6 h-6" />,
      color: 'from-amber-500 to-yellow-500',
      data: testDataCollection.chinaRealEstate
    },
    {
      id: 'aiTech',
      title: '生成式AI技术',
      description: '低风险场景 - 科技创新',
      icon: <Cpu className="w-6 h-6" />,
      color: 'from-green-500 to-emerald-500',
      data: testDataCollection.aiTech
    },
    {
      id: 'minimal',
      title: '最小化数据',
      description: '只包含标题的极简示例',
      icon: <Minimize2 className="w-6 h-6" />,
      color: 'from-slate-500 to-gray-500',
      data: testDataCollection.minimal
    },
    {
      id: 'topologyOnly',
      title: '供应链中断',
      description: '只有拓扑关系的示例',
      icon: <Network className="w-6 h-6" />,
      color: 'from-purple-500 to-violet-500',
      data: testDataCollection.topologyOnly
    },
    {
      id: 'temporalOnly',
      title: '全球气候变化',
      description: '只有时间动态的示例',
      icon: <Globe className="w-6 h-6" />,
      color: 'from-blue-500 to-cyan-500',
      data: testDataCollection.temporalOnly
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* 顶部导航 */}
      <nav className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <Home className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">CausalFlow</h1>
                <p className="text-xs text-slate-400">NodeDetailDrawer 组件演示</p>
              </div>
            </div>
            <div className="text-sm text-slate-400">
              点击卡片查看详情
            </div>
          </div>
        </div>
      </nav>

      {/* 主内容区 */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* 介绍区 */}
        <div className="mb-12 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            节点详情抽屉组件
          </h2>
          <p className="text-lg text-slate-300 max-w-2xl mx-auto">
            专业的商业情报风格详情面板，支持元信息、因果拓扑、时空动态和证据信源四大核心区块
          </p>
        </div>

        {/* 场景卡片网格 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {scenarios.map((scenario) => (
            <button
              key={scenario.id}
              onClick={() => handleCardClick(scenario.data)}
              className="group relative bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 text-left transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:border-slate-600"
            >
              {/* 渐变背景 */}
              <div className={`absolute inset-0 bg-gradient-to-br ${scenario.color} opacity-0 group-hover:opacity-10 rounded-xl transition-opacity duration-300`} />
              
              {/* 图标 */}
              <div className={`w-12 h-12 bg-gradient-to-br ${scenario.color} rounded-lg flex items-center justify-center mb-4 text-white shadow-lg`}>
                {scenario.icon}
              </div>

              {/* 标题 */}
              <h3 className="text-lg font-bold text-white mb-2 group-hover:text-purple-300 transition-colors">
                {scenario.title}
              </h3>

              {/* 描述 */}
              <p className="text-sm text-slate-400 leading-relaxed">
                {scenario.description}
              </p>

              {/* 箭头指示 */}
              <div className="mt-4 flex items-center gap-2 text-xs text-slate-500 group-hover:text-purple-400 transition-colors">
                <span>查看详情</span>
                <span className="group-hover:translate-x-1 transition-transform">→</span>
              </div>
            </button>
          ))}
        </div>

        {/* 功能特性 */}
        <div className="bg-slate-800/30 backdrop-blur-sm border border-slate-700 rounded-xl p-8">
          <h3 className="text-2xl font-bold text-white mb-6">核心特性</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex gap-4">
              <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-2xl">🎯</span>
              </div>
              <div>
                <h4 className="font-semibold text-white mb-1">商业情报风格</h4>
                <p className="text-sm text-slate-400">专业的视觉层次和信息密度设计</p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-2xl">⏱️</span>
              </div>
              <div>
                <h4 className="font-semibold text-white mb-1">时间轴可视化</h4>
                <p className="text-sm text-slate-400">垂直时间轴展示过去-现在-未来</p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-2xl">📊</span>
              </div>
              <div>
                <h4 className="font-semibold text-white mb-1">场景分析</h4>
                <p className="text-sm text-slate-400">Base Case 和 Tail Risk 双场景推演</p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-10 h-10 bg-amber-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-2xl">🔗</span>
              </div>
              <div>
                <h4 className="font-semibold text-white mb-1">信源追溯</h4>
                <p className="text-sm text-slate-400">展示新闻来源和 AI 置信度</p>
              </div>
            </div>
          </div>
        </div>

        {/* 技术栈 */}
        <div className="mt-8 text-center">
          <div className="inline-flex items-center gap-3 bg-slate-800/30 backdrop-blur-sm border border-slate-700 rounded-full px-6 py-3">
            <span className="text-sm text-slate-400">技术栈:</span>
            <div className="flex items-center gap-3">
              <span className="px-3 py-1 bg-blue-500/20 text-blue-300 text-xs font-medium rounded-full">React 18</span>
              <span className="px-3 py-1 bg-cyan-500/20 text-cyan-300 text-xs font-medium rounded-full">Tailwind CSS</span>
              <span className="px-3 py-1 bg-purple-500/20 text-purple-300 text-xs font-medium rounded-full">Lucide React</span>
            </div>
          </div>
        </div>
      </main>

      {/* NodeDetailDrawer 组件 */}
      <NodeDetailDrawer
        nodeData={selectedData}
        isOpen={isDrawerOpen}
        onClose={handleCloseDrawer}
      />
    </div>
  )
}

export default NodeDetailDrawerDemo












