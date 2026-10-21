import { useMemo, useState } from 'react'
import { Plus, Search, Trash2, WandSparkles } from 'lucide-react'

const INPUT_TYPES = [
  { value: 'event', label: '事件' },
  { value: 'data', label: '数据' },
  { value: 'news', label: '新闻' },
  { value: 'query', label: '问题' },
]

const DEFAULT_INPUTS = [
  { type: 'event', content: '美联储暂停加息' },
  { type: 'event', content: '日元套息交易平仓' },
  { type: 'event', content: '中国房地产危机加深' },
  { type: 'data', content: '全球黄金 ETF 持仓创新高' },
]

function QueryPanel({ loading, onSynthesize, onDeepAnalyze }) {
  const [inputs, setInputs] = useState(DEFAULT_INPUTS)
  const [maxDepth, setMaxDepth] = useState(5)
  const [mode, setMode] = useState('synthesize')

  const validInputs = useMemo(
    () => inputs.map((item) => ({ ...item, content: item.content.trim() })).filter((item) => item.content),
    [inputs],
  )

  const updateInput = (index, patch) => {
    setInputs((prev) => prev.map((item, idx) => (idx === index ? { ...item, ...patch } : item)))
  }

  const addInput = () => {
    setInputs((prev) => [...prev, { type: 'event', content: '' }])
  }

  const removeInput = (index) => {
    setInputs((prev) => (prev.length <= 1 ? prev : prev.filter((_, idx) => idx !== index)))
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    if (validInputs.length === 0) return
    if (mode === 'deep') {
      onDeepAnalyze({ seedQuery: validInputs[0].content, maxDepth })
      return
    }
    onSynthesize({ inputs: validInputs, maxDepth })
  }

  return (
    <form onSubmit={handleSubmit} className="min-h-0 space-y-6">
      <div>
        <div className="mb-3 flex rounded-md border border-zinc-200 bg-zinc-50 p-1">
          <button
            type="button"
            onClick={() => setMode('synthesize')}
            className={`flex-1 rounded px-3 py-2 text-sm ${mode === 'synthesize' ? 'bg-white text-slate-900 shadow-card' : 'text-slate-500'}`}
          >
            多输入综合
          </button>
          <button
            type="button"
            onClick={() => setMode('deep')}
            className={`flex-1 rounded px-3 py-2 text-sm ${mode === 'deep' ? 'bg-white text-slate-900 shadow-card' : 'text-slate-500'}`}
          >
            深度扩展
          </button>
        </div>
        <p className="text-xs leading-relaxed text-slate-500">
          {mode === 'synthesize'
            ? '输入多条看似不相关的信息，系统会寻找桥接节点和共同影响目标。'
            : '使用第一条输入作为种子，按层迭代扩展因果图谱。'}
        </p>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs font-medium text-slate-500">输入线索</label>
          <button
            type="button"
            onClick={addInput}
            className="inline-flex items-center gap-1.5 rounded-md border border-zinc-200 bg-white px-2.5 py-1.5 text-xs text-slate-700"
          >
            <Plus className="h-3.5 w-3.5" />
            添加
          </button>
        </div>

        {inputs.map((item, index) => (
          <div key={index} className="rounded-md border border-zinc-200 bg-white p-3">
            <div className="mb-2 flex items-center gap-2">
              <select
                value={item.type}
                onChange={(event) => updateInput(index, { type: event.target.value })}
                className="h-8 rounded-md border border-zinc-200 bg-zinc-50 px-2 text-xs text-slate-700"
              >
                {INPUT_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={() => removeInput(index)}
                className="ml-auto inline-flex h-8 w-8 items-center justify-center rounded-md text-slate-400 hover:bg-zinc-50 hover:text-slate-700"
                title="删除"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
            <textarea
              value={item.content}
              onChange={(event) => updateInput(index, { content: event.target.value })}
              placeholder={mode === 'deep' && index === 0 ? '例如：黄金价格' : '输入事件、数据或问题'}
              rows={2}
              className="w-full resize-none rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm leading-relaxed text-slate-800 placeholder:text-slate-400"
            />
          </div>
        ))}
      </div>

      <div>
        <div className="mb-3 flex items-center justify-between">
          <label className="text-xs font-medium text-slate-500">分析深度</label>
          <span className="font-mono text-sm text-slate-800">{maxDepth}</span>
        </div>
        <input
          type="range"
          min="1"
          max="8"
          value={maxDepth}
          onChange={(event) => setMaxDepth(Number(event.target.value))}
          className="w-full accent-slate-900"
        />
        <div className="mt-1 flex justify-between font-mono text-[11px] text-slate-400">
          <span>1</span>
          <span>8</span>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || validInputs.length === 0}
        className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-slate-900 px-4 py-3 text-sm font-medium text-white disabled:bg-zinc-200 disabled:text-slate-400"
      >
        {mode === 'synthesize' ? <WandSparkles className="h-4 w-4" /> : <Search className="h-4 w-4" />}
        {loading ? '分析中' : mode === 'synthesize' ? '综合分析' : '深度分析'}
      </button>
    </form>
  )
}

export default QueryPanel
