import { Handle, Position } from '@xyflow/react'
import { memo } from 'react'
import { Database, TrendingDown, TrendingUp } from 'lucide-react'

const ROLE_LABELS = {
  cause: '驱动',
  effect: '结果',
  intermediate: '桥接',
  target: '目标',
}

function CustomNode({ data, selected }) {
  const confidence = Number(data.confidence ?? 0.5)
  const realtime = data.realtime_state
  const hasValue = realtime?.latest_value && realtime.latest_value !== 'pending'
  const trend = realtime?.trend || 'stable'

  return (
    <div
      className={`relative h-[132px] w-[244px] overflow-hidden rounded-md border bg-white shadow-card ${
        selected ? 'border-slate-500 ring-2 ring-slate-200' : 'border-zinc-200'
      } ${data.dimmed ? 'opacity-35' : 'opacity-100'}`}
    >
      <div className="absolute inset-y-0 left-0 w-1" style={{ backgroundColor: data.accentColor || '#64748b' }} />
      <Handle type="target" position={Position.Left} className="!h-2 !w-2 !border-0 !bg-slate-400" />

      <div className="flex h-full flex-col p-4 pl-5">
        <div className="mb-2 flex items-center justify-between gap-3">
          <span className="max-w-[140px] truncate rounded bg-zinc-100 px-2 py-1 text-[11px] text-slate-600">
            {ROLE_LABELS[data.causal_role] || data.causal_role || '节点'}
          </span>
          <span className="font-mono text-[11px] text-slate-400">{Math.round(confidence * 100)}%</span>
        </div>

        <div className="line-clamp-2 text-sm font-semibold leading-snug text-slate-900">{data.label}</div>
        <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-slate-500">
          {data.description || data.cluster || data.domain || '暂无摘要'}
        </p>

        <div className="mt-auto flex items-center justify-between gap-3 pt-2">
          <span className="min-w-0 truncate text-[11px] text-slate-500">{data.cluster || data.domain || '未分类'}</span>
          {hasValue ? (
            <div className="flex max-w-[104px] items-center gap-1.5 rounded bg-zinc-50 px-2 py-1">
              <Database className="h-3 w-3 shrink-0 text-slate-400" />
              <span className="truncate font-mono text-[11px] text-slate-800">{realtime.latest_value}</span>
              {trend === 'rising' && <TrendingUp className="h-3 w-3 shrink-0 text-emerald-600" />}
              {trend === 'falling' && <TrendingDown className="h-3 w-3 shrink-0 text-red-600" />}
            </div>
          ) : null}
        </div>
      </div>

      <Handle type="source" position={Position.Right} className="!h-2 !w-2 !border-0 !bg-slate-400" />
    </div>
  )
}

export default memo(CustomNode)
