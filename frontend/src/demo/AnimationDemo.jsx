/**
 * 动画效果测试页面
 * 用于独立测试和演示动画效果
 */

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'

const ANIMATION_CONFIG = {
  graphScale: {
    type: "spring",
    stiffness: 300,
    damping: 30,
    mass: 0.8
  },
  graphTranslate: {
    type: "spring",
    stiffness: 280,
    damping: 28,
    mass: 0.9
  },
  blur: {
    type: "tween",
    duration: 0.3,
    ease: [0.4, 0, 0.2, 1]
  },
  drawer: {
    type: "spring",
    stiffness: 350,
    damping: 35,
    mass: 1
  }
}

function AnimationDemo() {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)

  return (
    <div className="w-full h-screen bg-slate-900 overflow-hidden">
      {/* 顶部控制栏 */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-50 bg-white/90 backdrop-blur-sm rounded-lg px-6 py-3 shadow-lg">
        <button
          onClick={() => setIsDrawerOpen(!isDrawerOpen)}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
        >
          {isDrawerOpen ? '关闭抽屉' : '打开抽屉'}
        </button>
        <span className="ml-4 text-sm text-slate-600">
          点击按钮或卡片查看动画效果
        </span>
      </div>

      {/* 模拟图谱容器 */}
      <motion.div
        className="w-full h-full flex items-center justify-center"
        animate={{
          scale: isDrawerOpen ? 0.75 : 1,
          x: isDrawerOpen ? '-15%' : '0%',
          filter: isDrawerOpen ? 'blur(4px)' : 'blur(0px)'
        }}
        transition={{
          scale: ANIMATION_CONFIG.graphScale,
          x: ANIMATION_CONFIG.graphTranslate,
          filter: ANIMATION_CONFIG.blur
        }}
        style={{
          transformOrigin: 'center center'
        }}
      >
        {/* 模拟图谱内容 */}
        <div className="relative">
          {/* 中心节点 */}
          <div className="flex items-center justify-center gap-8">
            {/* 左侧节点 */}
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsDrawerOpen(true)}
              className="w-40 h-32 bg-white rounded-lg shadow-lg border-l-4 border-orange-500 p-4 cursor-pointer"
            >
              <div className="text-xs font-semibold text-orange-700 bg-orange-100 px-2 py-1 rounded inline-block mb-2">
                原因
              </div>
              <div className="text-sm font-bold text-slate-800">
                美联储加息
              </div>
              <div className="text-xs text-slate-600 mt-2">
                置信度 85%
              </div>
            </motion.div>

            {/* 箭头 */}
            <div className="text-slate-400 text-2xl">→</div>

            {/* 中心节点 */}
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsDrawerOpen(true)}
              className="w-40 h-32 bg-white rounded-lg shadow-lg border-l-4 border-purple-500 p-4 cursor-pointer"
            >
              <div className="text-xs font-semibold text-purple-700 bg-purple-100 px-2 py-1 rounded inline-block mb-2">
                中间
              </div>
              <div className="text-sm font-bold text-slate-800">
                市场流动性
              </div>
              <div className="text-xs text-slate-600 mt-2">
                置信度 78%
              </div>
            </motion.div>

            {/* 箭头 */}
            <div className="text-slate-400 text-2xl">→</div>

            {/* 右侧节点 */}
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsDrawerOpen(true)}
              className="w-40 h-32 bg-white rounded-lg shadow-lg border-l-4 border-green-500 p-4 cursor-pointer"
            >
              <div className="text-xs font-semibold text-green-700 bg-green-100 px-2 py-1 rounded inline-block mb-2">
                结果
              </div>
              <div className="text-sm font-bold text-slate-800">
                股市波动
              </div>
              <div className="text-xs text-slate-600 mt-2">
                置信度 92%
              </div>
            </motion.div>
          </div>

          {/* 统计信息 */}
          <div className="absolute -bottom-16 left-1/2 -translate-x-1/2 bg-slate-800/90 backdrop-blur-sm rounded-lg px-4 py-2 text-white text-sm">
            节点数: 3 | 边数: 2
          </div>
        </div>
      </motion.div>

      {/* 抽屉和遮罩 */}
      <AnimatePresence mode="wait">
        {isDrawerOpen && (
          <>
            {/* 遮罩层 */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
              onClick={() => setIsDrawerOpen(false)}
            />

            {/* 抽屉面板 */}
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={ANIMATION_CONFIG.drawer}
              className="fixed right-0 top-0 h-screen w-[420px] bg-white shadow-2xl z-50 overflow-y-auto"
            >
              {/* 抽屉内容 */}
              <div className="p-6">
                {/* 头部 */}
                <div className="flex items-start justify-between mb-6">
                  <h2 className="text-2xl font-bold text-slate-900">
                    节点详情
                  </h2>
                  <button
                    onClick={() => setIsDrawerOpen(false)}
                    className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5 text-slate-600" />
                  </button>
                </div>

                {/* 标签 */}
                <div className="flex gap-2 mb-6">
                  <span className="px-3 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded-full">
                    中间节点
                  </span>
                  <span className="px-3 py-1 bg-amber-100 text-amber-700 text-xs font-medium rounded-full">
                    风险: 中
                  </span>
                </div>

                {/* 当前指标 */}
                <div className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl p-4 border border-slate-200 mb-6">
                  <div className="text-xs text-slate-600 font-medium mb-1">
                    市场流动性指数
                  </div>
                  <div className="text-3xl font-bold text-slate-900">
                    67.8
                  </div>
                  <div className="text-sm text-green-600 mt-2">
                    ↑ 上升趋势
                  </div>
                </div>

                {/* 因果链 */}
                <div className="mb-6">
                  <h3 className="text-sm font-bold text-slate-700 mb-3">
                    局部因果链
                  </h3>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="px-2.5 py-1 bg-orange-50 text-orange-700 rounded-md border border-orange-200 text-xs font-medium">
                      美联储加息
                    </span>
                    <span className="text-slate-400">→</span>
                    <span className="px-3 py-1.5 bg-purple-600 text-white rounded-md text-xs font-bold">
                      当前节点
                    </span>
                    <span className="text-slate-400">→</span>
                    <span className="px-2.5 py-1 bg-green-50 text-green-700 rounded-md border border-green-200 text-xs font-medium">
                      股市波动
                    </span>
                  </div>
                </div>

                {/* 描述 */}
                <div className="mb-6">
                  <h3 className="text-sm font-bold text-slate-700 mb-2">
                    节点描述
                  </h3>
                  <p className="text-sm text-slate-600 leading-relaxed">
                    市场流动性是指资产在市场上快速买卖而不引起价格大幅波动的能力。
                    当美联储加息时，市场流动性通常会收紧，进而影响股市表现。
                  </p>
                </div>

                {/* 置信度 */}
                <div>
                  <h3 className="text-sm font-bold text-slate-700 mb-3">
                    AI 置信度
                  </h3>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-slate-600">
                      分析可信度
                    </span>
                    <span className="text-sm font-bold text-slate-900">
                      78%
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                    <div
                      className="h-full bg-amber-500 transition-all duration-500"
                      style={{ width: '78%' }}
                    />
                  </div>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* 动画参数显示 */}
      <div className="absolute bottom-4 left-4 bg-slate-800/90 backdrop-blur-sm rounded-lg p-4 text-white text-xs space-y-2 max-w-xs">
        <div className="font-bold mb-2">动画参数</div>
        <div>缩放: {isDrawerOpen ? '75%' : '100%'}</div>
        <div>位移: {isDrawerOpen ? '-15%' : '0%'}</div>
        <div>模糊: {isDrawerOpen ? '4px' : '0px'}</div>
        <div className="pt-2 border-t border-slate-600">
          <div>弹簧刚度: 280-350</div>
          <div>阻尼系数: 28-35</div>
          <div>质量: 0.8-1.0</div>
        </div>
      </div>
    </div>
  )
}

export default AnimationDemo










