/**
 * 加载动画覆盖层组件
 * 显示流式处理的实时进度
 */

import { useEffect, useState } from 'react'

function LoadingOverlay({ isVisible, message, progress }) {
  const [dots, setDots] = useState('')

  // 动画点点点效果
  useEffect(() => {
    if (!isVisible) return

    const interval = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? '' : prev + '.'))
    }, 500)

    return () => clearInterval(interval)
  }, [isVisible])

  if (!isVisible) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-md">
      <div className="relative">
        {/* 发光背景效果 */}
        <div className="absolute inset-0 blur-3xl opacity-50">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-purple-500 via-pink-500 to-cyan-500 rounded-full animate-pulse" />
        </div>

        {/* 主内容卡片 */}
        <div className="relative bg-slate-900/90 backdrop-blur-xl rounded-3xl border border-white/10 shadow-2xl p-12 min-w-[500px]">
          {/* 心跳动画圆环 */}
          <div className="flex justify-center mb-8">
            <div className="relative">
              {/* 外圈 - 脉冲效果 */}
              <div className="absolute inset-0 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 opacity-20 animate-ping" />
              
              {/* 中圈 - 旋转效果 */}
              <div className="relative w-24 h-24 rounded-full border-4 border-transparent bg-gradient-to-r from-purple-500 via-pink-500 to-cyan-500 animate-spin">
                <div className="absolute inset-1 rounded-full bg-slate-900" />
              </div>
              
              {/* 内圈 - 发光核心 */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-12 h-12 rounded-full bg-gradient-to-r from-purple-400 to-pink-400 animate-pulse shadow-lg shadow-purple-500/50" />
              </div>
            </div>
          </div>

          {/* 进度文字 */}
          <div className="text-center space-y-4">
            <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400">
              {message || '处理中'}{dots}
            </h3>

            {/* 进度详情 */}
            {progress && (
              <div className="space-y-3 mt-6">
                {/* 步骤指示器 */}
                <div className="flex justify-center gap-2">
                  <StepIndicator 
                    active={progress.status.includes('step1')} 
                    completed={progress.status === 'step2_start' || progress.status === 'step2_complete' || progress.status === 'step3_start' || progress.status === 'step3_complete' || progress.status === 'success'}
                    label="1"
                  />
                  <StepIndicator 
                    active={progress.status.includes('step2')} 
                    completed={progress.status === 'step3_start' || progress.status === 'step3_complete' || progress.status === 'success'}
                    label="2"
                  />
                  <StepIndicator 
                    active={progress.status.includes('step3')} 
                    completed={progress.status === 'success'}
                    label="3"
                  />
                </div>

                {/* 步骤说明 */}
                <div className="text-sm text-slate-400 space-y-1">
                  {progress.data && (
                    <>
                      {progress.data.factors && (
                        <div className="text-xs">
                          核心因子: {progress.data.factors.slice(0, 3).join('、')}
                          {progress.data.factors.length > 3 && '...'}
                        </div>
                      )}
                      {progress.data.elapsed && (
                        <div className="text-xs text-slate-500">
                          耗时: {progress.data.elapsed.toFixed(1)}秒
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            )}

            {/* 提示文字 */}
            <p className="text-sm text-slate-500 mt-6">
              正在调用大模型和搜索引擎，请稍候...
            </p>
          </div>

          {/* 装饰性粒子效果 */}
          <div className="absolute inset-0 overflow-hidden rounded-3xl pointer-events-none">
            {[...Array(20)].map((_, i) => (
              <div
                key={i}
                className="absolute w-1 h-1 bg-white rounded-full opacity-20"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  animation: `float ${3 + Math.random() * 4}s ease-in-out infinite`,
                  animationDelay: `${Math.random() * 2}s`,
                }}
              />
            ))}
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0) translateX(0);
            opacity: 0.2;
          }
          50% {
            transform: translateY(-20px) translateX(10px);
            opacity: 0.5;
          }
        }
      `}</style>
    </div>
  )
}

/**
 * 步骤指示器组件
 */
function StepIndicator({ active, completed, label }) {
  return (
    <div className="flex flex-col items-center gap-1">
      <div
        className={`
          w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm
          transition-all duration-300
          ${completed 
            ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg shadow-green-500/50' 
            : active 
            ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-500/50 animate-pulse' 
            : 'bg-slate-700 text-slate-500'
          }
        `}
      >
        {completed ? (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        ) : (
          label
        )}
      </div>
    </div>
  )
}

export default LoadingOverlay







