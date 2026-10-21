import { useMemo, useState } from 'react'
import { Activity, Database, GitBranch, Layers3, Pause, RotateCcw, Sparkles } from 'lucide-react'
import CausalGraph from './components/CausalGraph'
import QueryPanel from './components/QueryPanel'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v2'

async function streamPost(url, body, onEvent) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  if (!response.ok || !response.body) {
    const text = await response.text()
    throw new Error(text || '请求失败')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const chunks = buffer.split('\n\n')
    buffer = chunks.pop() || ''

    for (const chunk of chunks) {
      const line = chunk.split('\n').find((item) => item.startsWith('data:'))
      if (!line) continue
      const payload = line.replace(/^data:\s*/, '')
      onEvent(JSON.parse(payload))
    }
  }
}

function App() {
  const [session, setSession] = useState(null)
  const [graphData, setGraphData] = useState(null)
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedNode, setSelectedNode] = useState(null)
  const [error, setError] = useState('')

  const stats = useMemo(() => {
    const nodes = graphData?.nodes || []
    const edges = graphData?.edges || []
    const sources = nodes.reduce((count, node) => count + (node.realtime_state?.sources?.length || 0), 0)
    const clusters = graphData?.clusters?.length || new Set(nodes.map((node) => node.cluster).filter(Boolean)).size
    return { nodes: nodes.length, edges: edges.length, sources, clusters }
  }, [graphData])

  const ensureSession = async (title) => {
    if (session?.id) return session
    const response = await fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    })
    if (!response.ok) throw new Error('创建会话失败')
    const nextSession = await response.json()
    setSession(nextSession)
    return nextSession
  }

  const handleSynthesize = async ({ inputs, maxDepth }) => {
    setLoading(true)
    setError('')
    setEvents([])
    setSelectedNode(null)

    try {
      const title = inputs.find((item) => item.content.trim())?.content || '宏观多输入分析'
      const activeSession = await ensureSession(title)
      await streamPost(
        `${API_BASE}/sessions/${activeSession.id}/synthesize`,
        {
          inputs,
          find_connections: true,
          discover_targets: true,
          max_depth: maxDepth,
        },
        (event) => {
          setEvents((prev) => [event, ...prev].slice(0, 24))
          const graph = event.data?.graph
          if (graph) setGraphData(graph)
          if (event.data?.session) setSession(event.data.session)
        },
      )
    } catch (err) {
      setError(err.message || '分析失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDeepAnalyze = async ({ seedQuery, maxDepth }) => {
    setLoading(true)
    setError('')
    setEvents([])

    try {
      const activeSession = await ensureSession(seedQuery)
      await streamPost(
        `${API_BASE}/sessions/${activeSession.id}/analyze-deep`,
        { seed_query: seedQuery, max_depth: maxDepth, max_nodes: 50 },
        (event) => {
          setEvents((prev) => [event, ...prev].slice(0, 24))
          const graph = event.data?.graph
          if (graph) setGraphData(graph)
          if (event.data?.session) setSession(event.data.session)
        },
      )
    } catch (err) {
      setError(err.message || '深度分析失败')
    } finally {
      setLoading(false)
    }
  }

  const handleExpandNode = async (direction = 'both') => {
    if (!session?.id || !selectedNode?.id) return
    setLoading(true)
    setError('')
    try {
      const response = await fetch(`${API_BASE}/sessions/${session.id}/expand`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ node_id: selectedNode.id, direction }),
      })
      if (!response.ok) throw new Error('节点扩展失败')
      const data = await response.json()
      setGraphData(data.graph)
      setSession(data.session)
      setEvents((prev) => [
        { status: 'expand', message: `已围绕「${selectedNode.label}」新增 ${data.delta.nodes.length} 个节点`, timestamp: new Date().toISOString(), data },
        ...prev,
      ].slice(0, 24))
    } catch (err) {
      setError(err.message || '节点扩展失败')
    } finally {
      setLoading(false)
    }
  }

  const handleUndo = async () => {
    if (!session?.id) return
    const response = await fetch(`${API_BASE}/sessions/${session.id}/undo`, { method: 'POST' })
    if (!response.ok) return
    const nextSession = await response.json()
    setSession(nextSession)
    setGraphData(nextSession.graph)
    setEvents((prev) => [{ status: 'undo', message: '已回退到上一个图谱状态', timestamp: new Date().toISOString(), data: {} }, ...prev])
  }

  return (
    <div className="h-screen w-screen overflow-hidden bg-zinc-50 text-slate-900">
      <div className="grid h-full min-h-0 grid-cols-[360px_minmax(0,1fr)_340px]">
        <aside className="min-h-0 overflow-hidden border-r border-zinc-200 bg-white">
          <div className="flex h-full min-h-0 flex-col">
            <div className="border-b border-zinc-200 px-6 py-5">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-md bg-slate-900 text-white">
                  <GitBranch className="h-4 w-4" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold tracking-normal">CausalFlow v2</h1>
                  <p className="text-xs text-slate-500">宏观经济因果分析引擎</p>
                </div>
              </div>
            </div>

            <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-6 py-5 pb-24">
              <QueryPanel
                loading={loading}
                onSynthesize={handleSynthesize}
                onDeepAnalyze={handleDeepAnalyze}
              />
            </div>
          </div>
        </aside>

        <main className="relative min-h-0 min-w-0 overflow-hidden bg-white">
          <div className="absolute left-5 top-5 z-20 flex items-center gap-2 rounded-md border border-zinc-200 bg-white/90 px-3 py-2 shadow-panel backdrop-blur">
            <Activity className={`h-4 w-4 ${loading ? 'animate-pulse text-emerald-600' : 'text-slate-500'}`} />
            <span className="text-sm text-slate-700">{loading ? '分析进行中' : graphData ? '图谱就绪' : '等待输入'}</span>
            {loading && <Pause className="h-4 w-4 text-slate-400" />}
          </div>

          {graphData ? (
            <CausalGraph
              data={graphData}
              selectedNode={selectedNode}
              onSelectNode={setSelectedNode}
              onExpandNode={handleExpandNode}
            />
          ) : (
            <div className="flex h-full items-center justify-center">
              <div className="text-center">
                <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-md border border-zinc-200 bg-zinc-50">
                  <Layers3 className="h-6 w-6 text-slate-500" />
                </div>
                <p className="text-base font-medium text-slate-800">输入多条宏观线索，生成因果图谱</p>
                <p className="mt-2 text-sm text-slate-500">SSE 会逐层推送子图、桥接节点、共同目标和数据填充结果。</p>
              </div>
            </div>
          )}
        </main>

        <aside className="min-h-0 overflow-hidden border-l border-zinc-200 bg-zinc-50">
          <div className="flex h-full min-h-0 flex-col">
            <div className="border-b border-zinc-200 px-6 py-5">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold">分析面板</h2>
                <button
                  type="button"
                  onClick={handleUndo}
                  disabled={!session?.id || loading}
                  className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-zinc-200 bg-white text-slate-600 disabled:opacity-40"
                  title="撤销"
                >
                  <RotateCcw className="h-4 w-4" />
                </button>
              </div>
            </div>

            <div className="min-h-0 flex-1 space-y-5 overflow-y-auto overscroll-contain px-6 py-5 pb-24">
              {error && (
                <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                  {error}
                </div>
              )}

              <div className="grid grid-cols-2 gap-3">
                <Metric icon={Layers3} label="节点" value={stats.nodes} />
                <Metric icon={GitBranch} label="关系" value={stats.edges} />
                <Metric icon={Database} label="来源" value={stats.sources} />
                <Metric icon={Sparkles} label="聚类" value={stats.clusters} />
              </div>

              {selectedNode && (
                <section className="rounded-md border border-zinc-200 bg-white p-4">
                  <div className="mb-3 text-xs font-medium text-slate-500">当前节点</div>
                  <h3 className="text-base font-semibold leading-snug">{selectedNode.label}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-600">{selectedNode.description || '暂无描述'}</p>
                  <div className="mt-4 grid grid-cols-3 gap-2">
                    <button onClick={() => handleExpandNode('causes')} className="rounded-md bg-slate-900 px-2 py-2 text-xs text-white">原因</button>
                    <button onClick={() => handleExpandNode('effects')} className="rounded-md bg-slate-700 px-2 py-2 text-xs text-white">影响</button>
                    <button onClick={() => handleExpandNode('both')} className="rounded-md bg-emerald-700 px-2 py-2 text-xs text-white">相关</button>
                  </div>
                </section>
              )}

              <section>
                <div className="mb-3 text-xs font-medium text-slate-500">事件流</div>
                <div className="space-y-3">
                  {events.length === 0 ? (
                    <p className="text-sm text-slate-500">分析开始后会显示每层进度。</p>
                  ) : (
                    events.map((event, index) => (
                      <div key={`${event.timestamp}-${index}`} className="rounded-md border border-zinc-200 bg-white px-3 py-3">
                        <div className="flex items-center justify-between gap-3">
                          <span className="text-xs font-medium uppercase tracking-normal text-emerald-700">{event.status}</span>
                          <span className="text-[11px] text-slate-400">{new Date(event.timestamp).toLocaleTimeString('zh-CN')}</span>
                        </div>
                        <p className="mt-1 text-sm leading-relaxed text-slate-700">{event.message}</p>
                      </div>
                    ))
                  )}
                </div>
              </section>

              {graphData?.explanation && (
                <section>
                  <div className="mb-3 text-xs font-medium text-slate-500">综合解释</div>
                  <p className="text-sm leading-relaxed text-slate-700">{graphData.explanation}</p>
                </section>
              )}
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}

function Metric({ icon: Icon, label, value }) {
  return (
    <div className="rounded-md border border-zinc-200 bg-white p-3">
      <div className="mb-2 flex items-center gap-2 text-xs text-slate-500">
        <Icon className="h-3.5 w-3.5" />
        {label}
      </div>
      <div className="font-mono text-2xl text-slate-900">{value}</div>
    </div>
  )
}

export default App
