import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Background,
  Controls,
  MarkerType,
  MiniMap,
  ReactFlow,
  useEdgesState,
  useNodesState,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { Maximize2, Network, RefreshCw } from 'lucide-react'
import CustomNode from './CustomNode'

const nodeTypes = { customNode: CustomNode }

const DOMAIN_COLORS = {
  monetary_policy: '#0f766e',
  currency: '#2563eb',
  liquidity: '#7c3aed',
  geopolitics: '#b91c1c',
  market: '#c2410c',
  structure: '#475569',
}

const NODE_WIDTH = 244
const NODE_HEIGHT = 132
const LAYER_GAP = 360
const ROW_GAP = 170
const CLUSTER_GAP = 54

function inferLayer(node) {
  if (Number.isFinite(Number(node.layer))) return Number(node.layer)
  if (node.causal_role === 'cause') return 0
  if (node.causal_role === 'effect' || node.causal_role === 'target') return 3
  return 1
}

function normalizeCluster(node) {
  return node.cluster || node.domain || '其他'
}

function buildLayeredLayout(nodes, activeCluster) {
  const visibleNodes = activeCluster
    ? nodes.filter((node) => normalizeCluster(node) === activeCluster)
    : nodes

  const layers = new Map()
  visibleNodes.forEach((node) => {
    const layer = inferLayer(node)
    if (!layers.has(layer)) layers.set(layer, [])
    layers.get(layer).push(node)
  })

  const sortedLayers = Array.from(layers.keys()).sort((a, b) => a - b)
  const layerIndexByValue = new Map(sortedLayers.map((layer, index) => [layer, index]))
  const laidOut = []

  sortedLayers.forEach((layer) => {
    const layerNodes = layers.get(layer)
    const clusterGroups = new Map()

    layerNodes
      .slice()
      .sort((a, b) => normalizeCluster(a).localeCompare(normalizeCluster(b), 'zh-CN'))
      .forEach((node) => {
        const cluster = normalizeCluster(node)
        if (!clusterGroups.has(cluster)) clusterGroups.set(cluster, [])
        clusterGroups.get(cluster).push(node)
      })

    let yCursor = 0
    Array.from(clusterGroups.entries()).forEach(([cluster, clusterNodes]) => {
      clusterNodes
        .slice()
        .sort((a, b) => Number(b.confidence || 0) - Number(a.confidence || 0))
        .forEach((node) => {
          laidOut.push({
            id: node.id,
            type: 'customNode',
            data: {
              ...node,
              accentColor: DOMAIN_COLORS[node.domain] || '#64748b',
              cluster,
              dimmed: false,
            },
            position: {
              x: (layerIndexByValue.get(layer) || 0) * LAYER_GAP,
              y: yCursor,
            },
            width: NODE_WIDTH,
            height: NODE_HEIGHT,
            draggable: true,
          })
          yCursor += ROW_GAP
        })
      yCursor += CLUSTER_GAP
    })
  })

  return laidOut
}

function pickBackboneEdges(edges, visibleNodeIds) {
  const candidates = edges.filter((edge) => visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target))
  const byTarget = new Map()

  candidates.forEach((edge) => {
    const list = byTarget.get(edge.target) || []
    list.push(edge)
    byTarget.set(edge.target, list)
  })

  const chosen = new Map()
  byTarget.forEach((list) => {
    list
      .slice()
      .sort((a, b) => Number(b.confidence || b.strength || 0) - Number(a.confidence || a.strength || 0))
      .slice(0, 2)
      .forEach((edge) => chosen.set(edge.id || `${edge.source}-${edge.target}`, edge))
  })

  candidates
    .filter((edge) => Number(edge.confidence || edge.strength || 0) >= 0.74)
    .forEach((edge) => chosen.set(edge.id || `${edge.source}-${edge.target}`, edge))

  return Array.from(chosen.values()).slice(0, 70)
}

function buildFlowEdges(rawEdges, visibleNodeIds, selectedNodeId, edgeMode) {
  const visibleEdges = rawEdges.filter((edge) => visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target))
  let displayEdges = visibleEdges

  if (edgeMode === 'focus' && selectedNodeId) {
    displayEdges = visibleEdges.filter((edge) => edge.source === selectedNodeId || edge.target === selectedNodeId)
  } else if (edgeMode !== 'all') {
    displayEdges = pickBackboneEdges(rawEdges, visibleNodeIds)
  }

  return displayEdges.map((edge) => {
    const connected = selectedNodeId && (edge.source === selectedNodeId || edge.target === selectedNodeId)
    const strength = Number(edge.strength || edge.confidence || 0.5)
    const isMuted = selectedNodeId && edgeMode === 'all' && !connected
    const stroke = connected ? '#0f172a' : edgeMode === 'all' ? '#d4d4d8' : '#94a3b8'

    return {
      id: edge.id || `${edge.source}-${edge.target}`,
      source: edge.source,
      target: edge.target,
      label: connected ? edge.label || '' : '',
      type: 'smoothstep',
      animated: connected,
      interactionWidth: 24,
      style: {
        stroke,
        strokeOpacity: isMuted ? 0.25 : connected ? 0.95 : 0.55,
        strokeWidth: connected ? 2.3 : Math.max(1, strength * 1.8),
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: stroke,
        width: connected ? 18 : 13,
        height: connected ? 18 : 13,
      },
      labelStyle: { fill: '#475569', fontSize: 11, fontWeight: 500 },
      labelBgStyle: { fill: '#ffffff', fillOpacity: 0.92 },
    }
  })
}

function CausalGraph({ data, selectedNode, onSelectNode, onExpandNode }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [edgeMode, setEdgeMode] = useState('main')
  const [activeCluster, setActiveCluster] = useState('')

  const sourceNodes = data?.nodes || []
  const sourceEdges = data?.edges || []
  const selectedNodeId = selectedNode?.id

  const clusters = useMemo(() => {
    const counts = new Map()
    sourceNodes.forEach((node) => {
      const cluster = normalizeCluster(node)
      counts.set(cluster, (counts.get(cluster) || 0) + 1)
    })
    return Array.from(counts.entries()).map(([label, count]) => ({ label, count }))
  }, [sourceNodes])

  useEffect(() => {
    if (!sourceNodes.length) return

    const flowNodes = buildLayeredLayout(sourceNodes, activeCluster).map((node) => {
      const isConnected =
        !selectedNodeId ||
        node.id === selectedNodeId ||
        sourceEdges.some(
          (edge) =>
            (edge.source === selectedNodeId && edge.target === node.id) ||
            (edge.target === selectedNodeId && edge.source === node.id),
        )

      return {
        ...node,
        data: {
          ...node.data,
          dimmed: Boolean(selectedNodeId && !isConnected),
        },
      }
    })

    const visibleNodeIds = new Set(flowNodes.map((node) => node.id))
    setNodes(flowNodes)
    setEdges(buildFlowEdges(sourceEdges, visibleNodeIds, selectedNodeId, edgeMode))
  }, [activeCluster, edgeMode, selectedNodeId, setEdges, setNodes, sourceEdges, sourceNodes])

  const handleNodeClick = useCallback(
    (_, node) => {
      onSelectNode?.(sourceNodes.find((item) => item.id === node.id) || node.data)
      setEdgeMode('focus')
    },
    [onSelectNode, sourceNodes],
  )

  const handlePaneClick = useCallback(() => {
    onSelectNode?.(null)
    setEdgeMode('main')
  }, [onSelectNode])

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        onPaneClick={handlePaneClick}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.16, minZoom: 0.45, maxZoom: 0.9 }}
        minZoom={0.18}
        maxZoom={1.5}
        defaultEdgeOptions={{ type: 'smoothstep' }}
        attributionPosition="bottom-left"
      >
        <Background variant="dots" gap={28} size={0.9} color="#e4e4e7" />
        <Controls showInteractive={false} />
        <MiniMap
          nodeColor={(node) => node.data?.accentColor || '#64748b'}
          maskColor="rgba(250,250,250,0.72)"
          pannable
          zoomable
        />
      </ReactFlow>

      <div className="absolute left-5 top-16 z-20 flex max-w-[calc(100%-380px)] flex-wrap gap-2">
        <button
          type="button"
          onClick={() => setActiveCluster('')}
          className={`rounded-md border px-3 py-2 text-xs shadow-card backdrop-blur ${
            activeCluster ? 'border-zinc-200 bg-white/90 text-slate-600' : 'border-slate-300 bg-slate-900 text-white'
          }`}
        >
          全部
        </button>
        {clusters.map((cluster) => (
          <button
            key={cluster.label}
            type="button"
            onClick={() => setActiveCluster(cluster.label)}
            className={`rounded-md border px-3 py-2 text-xs shadow-card backdrop-blur ${
              activeCluster === cluster.label
                ? 'border-slate-300 bg-slate-900 text-white'
                : 'border-zinc-200 bg-white/90 text-slate-600'
            }`}
          >
            {cluster.label}
            <span className="ml-2 font-mono opacity-70">{cluster.count}</span>
          </button>
        ))}
      </div>

      <div className="absolute bottom-5 left-5 z-20 flex rounded-md border border-zinc-200 bg-white/95 p-1 shadow-panel backdrop-blur">
        {[
          ['main', '主干'],
          ['focus', '聚焦'],
          ['all', '全部边'],
        ].map(([value, label]) => (
          <button
            key={value}
            type="button"
            onClick={() => setEdgeMode(value)}
            className={`rounded px-3 py-2 text-xs ${
              edgeMode === value ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-zinc-100'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {selectedNode && (
        <div className="absolute right-5 top-20 z-20 w-[300px] rounded-md border border-zinc-200 bg-white/95 p-4 shadow-panel backdrop-blur">
          <div className="mb-2 flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
              <Network className="h-3.5 w-3.5" />
              节点钻取
            </div>
            <span className="rounded bg-zinc-100 px-2 py-1 text-[11px] text-slate-500">
              {selectedNode.cluster || selectedNode.domain}
            </span>
          </div>
          <h3 className="text-base font-semibold leading-snug">{selectedNode.label}</h3>
          <p className="mt-2 line-clamp-3 text-sm leading-relaxed text-slate-600">{selectedNode.description}</p>
          {selectedNode.realtime_state && (
            <div className="mt-3 rounded-md bg-zinc-50 p-3">
              <div className="text-[11px] text-slate-500">实时状态</div>
              <div className="mt-1 font-mono text-sm text-slate-900">{selectedNode.realtime_state.latest_value}</div>
            </div>
          )}
          <div className="mt-4 flex gap-2">
            <button
              type="button"
              onClick={() => onExpandNode?.('both')}
              className="inline-flex flex-1 items-center justify-center gap-1.5 rounded-md bg-slate-900 px-3 py-2 text-xs text-white"
            >
              <Maximize2 className="h-3.5 w-3.5" />
              扩展
            </button>
            <button
              type="button"
              onClick={() => onExpandNode?.('causes')}
              className="inline-flex flex-1 items-center justify-center gap-1.5 rounded-md border border-zinc-200 bg-white px-3 py-2 text-xs text-slate-700"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              原因
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default CausalGraph
