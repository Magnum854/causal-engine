import { useState } from 'react'

const EXAMPLES = [
  '全球变暖会导致什么后果？',
  '经济衰退的原因是什么？',
  '人工智能发展对就业市场的影响',
]

function QueryPanel({ onAnalyze, loading }) {
  const [query, setQuery] = useState('')
  const [context, setContext] = useState('')
  const [maxDepth, setMaxDepth] = useState(3)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) {
      onAnalyze(query, context || null, maxDepth)
    }
  }

  const handleExampleClick = (example) => {
    setQuery(example)
  }

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6">
      <h2 className="text-lg font-semibold text-slate-900 mb-5">分析配置</h2>
      
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* 问题输入 */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            分析问题 <span className="text-red-500">*</span>
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="请输入您想要分析的因果问题..."
            className="w-full px-3 py-2.5 bg-white border border-slate-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:border-transparent transition-all resize-none text-sm"
            rows={4}
            required
          />
        </div>

        {/* 背景信息 */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            背景信息（可选）
          </label>
          <textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="提供额外的背景信息以获得更准确的分析..."
            className="w-full px-3 py-2.5 bg-white border border-slate-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:border-transparent transition-all resize-none text-sm"
            rows={3}
          />
        </div>

        {/* 深度控制 */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            分析深度：{maxDepth} 层
          </label>
          <input
            type="range"
            min="1"
            max="5"
            value={maxDepth}
            onChange={(e) => setMaxDepth(parseInt(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-slate-900"
          />
          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span>简单</span>
            <span>详细</span>
          </div>
        </div>

        {/* 提交按钮 */}
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="w-full py-2.5 px-4 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 text-white font-medium rounded-md transition-all duration-200 disabled:cursor-not-allowed shadow-sm text-sm"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              分析中...
            </span>
          ) : (
            '开始分析'
          )}
        </button>
      </form>

      {/* 示例问题 */}
      <div className="mt-6 pt-5 border-t border-slate-200">
        <h3 className="text-sm font-medium text-slate-700 mb-3">示例问题</h3>
        <div className="space-y-2">
          {EXAMPLES.map((example, index) => (
            <button
              key={index}
              onClick={() => handleExampleClick(example)}
              className="w-full text-left px-3 py-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 hover:border-slate-300 rounded-md text-sm text-slate-700 transition-all duration-200"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default QueryPanel

