/**
 * 节点详情抽屉组件 - 北欧极简风格
 * 克制与呼吸感 + 排版层级 + 物理隐喻
 */

import { X, TrendingUp, TrendingDown, AlertTriangle, Clock, ExternalLink, Target, Activity } from 'lucide-react'
import { motion } from 'framer-motion'

// 弹簧动画配置
const SPRING_CONFIG = {
  button: {
    type: "spring",
    stiffness: 400,
    damping: 25,
    mass: 0.5
  },
  card: {
    type: "spring",
    stiffness: 300,
    damping: 28,
    mass: 0.8
  }
}

/**
 * Header 组件 - 顶部元信息区
 */
function DrawerHeader({ meta, onClose }) {
  return (
    <div className="sticky top-0 bg-white/95 backdrop-blur-md border-b border-slate-100 p-10 z-10">
      {/* 标题行 */}
      <div className="flex items-start justify-between mb-8">
        <h2 className="text-2xl font-semibold text-slate-800 leading-snug pr-8 tracking-tight">
          {meta.title}
        </h2>
        <motion.button
          onClick={onClose}
          whileHover={{ scale: 1.05, rotate: 90 }}
          whileTap={{ scale: 0.95 }}
          transition={SPRING_CONFIG.button}
          className="p-2 hover:bg-slate-50 rounded-md flex-shrink-0"
          aria-label="关闭"
        >
          <X className="w-4 h-4 text-slate-400" strokeWidth={1.5} />
        </motion.button>
      </div>

      {/* 标签行 */}
      <div className="flex flex-wrap gap-2 mb-8">
        {meta.category && (
          <motion.span 
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={SPRING_CONFIG.card}
            className="px-3 py-1 bg-slate-100 text-slate-600 text-[10px] font-normal rounded tracking-wide uppercase"
          >
            {meta.category}
          </motion.span>
        )}
      </div>

      {/* 当前指标卡片 */}
      {meta.current_metric && (
        <motion.div 
          initial={{ y: 10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ ...SPRING_CONFIG.card, delay: 0.1 }}
          className="bg-slate-50 rounded-md p-6"
        >
          <div className="flex items-baseline justify-between">
            <div className="flex-1">
              <div className="text-[10px] text-slate-500 mb-3 tracking-wide font-normal uppercase">
                {meta.current_metric.label}
              </div>
              <div className="text-4xl font-mono text-slate-800 tracking-tight tabular-nums">
                {meta.current_metric.value}
              </div>
            </div>
            <div className="flex items-center gap-2">
              {meta.current_metric.trend === 'up' && (
                <motion.div 
                  initial={{ y: 5, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={SPRING_CONFIG.card}
                  className="flex items-center gap-2 text-slate-600"
                >
                  <TrendingUp className="w-5 h-5" strokeWidth={1.5} />
                  <span className="text-xs font-normal">上升</span>
                </motion.div>
              )}
              {meta.current_metric.trend === 'down' && (
                <motion.div 
                  initial={{ y: 5, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={SPRING_CONFIG.card}
                  className="flex items-center gap-2 text-slate-600"
                >
                  <TrendingDown className="w-5 h-5" strokeWidth={1.5} />
                  <span className="text-xs font-normal">下降</span>
                </motion.div>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}

/**
 * Topology 组件 - 因果脉络区
 */
function TopologySection({ topology }) {
  if (!topology) return null

  return (
    <div className="px-10 py-8 border-b border-slate-100">
      <h3 className="text-[10px] font-normal text-slate-500 mb-5 flex items-center gap-2 tracking-wide uppercase">
        <Target className="w-3.5 h-3.5" strokeWidth={1.5} />
        因果链
      </h3>
      
      <div className="flex items-center gap-3 flex-wrap text-sm">
        {/* 原因节点 */}
        {topology.causes && topology.causes.length > 0 && (
          <>
            <div className="flex gap-2">
              {topology.causes.map((cause, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1.5 bg-sky-50/50 text-sky-700 rounded text-xs font-normal"
                >
                  {cause}
                </span>
              ))}
            </div>
            <span className="text-slate-300 font-normal text-base">→</span>
          </>
        )}

        {/* 当前节点 */}
        <span className="px-3.5 py-1.5 bg-slate-800 text-white rounded text-xs font-normal">
          当前
        </span>

        {/* 结果节点 */}
        {topology.effects && topology.effects.length > 0 && (
          <>
            <span className="text-slate-300 font-normal text-base">→</span>
            <div className="flex gap-2">
              {topology.effects.map((effect, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1.5 bg-rose-50/50 text-rose-700 rounded text-xs font-normal"
                >
                  {effect}
                </span>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

/**
 * 场景卡片组件
 */
function ScenarioCard({ scenario, type }) {
  const isRisk = type === 'risk'
  
  const getTypeStyles = () => {
    if (isRisk) {
      return {
        bg: 'bg-rose-50/50',
        badge: 'bg-slate-800 text-white',
        icon: <AlertTriangle className="w-3.5 h-3.5" strokeWidth={1.5} />
      }
    }
    return {
      bg: 'bg-sky-50/50',
      badge: 'bg-slate-800 text-white',
      icon: <Activity className="w-3.5 h-3.5" strokeWidth={1.5} />
    }
  }

  const styles = getTypeStyles()

  return (
    <div className={`${styles.bg} rounded-md p-5 relative`}>
      {/* 概率标签 */}
      <div className="absolute top-4 right-4">
        <span className={`${styles.badge} px-2.5 py-1 rounded text-[10px] font-mono tabular-nums`}>
          {scenario.probability}
        </span>
      </div>

      {/* 标题 */}
      <div className="flex items-center gap-2.5 mb-4 pr-20">
        {styles.icon}
        <h4 className="font-normal text-sm text-slate-800">
          {scenario.title}
        </h4>
      </div>

      {/* 描述 */}
      <p className="text-sm text-slate-600 leading-relaxed mb-4 font-normal">
        {scenario.description}
      </p>

      {/* 关键指标 */}
      {scenario.key_metrics && scenario.key_metrics.length > 0 && (
        <div className="space-y-2.5">
          {scenario.key_metrics.map((metric, idx) => (
            <div key={idx} className="flex items-center justify-between text-sm">
              <span className="text-slate-500 font-normal">{metric.label}</span>
              <span className="font-mono text-slate-800 tabular-nums">{metric.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/**
 * 时间轴节点组件
 */
function TimelineNode({ phase, isActive, children }) {
  const getPhaseStyles = () => {
    switch (phase) {
      case 'past':
        return {
          dot: 'bg-slate-200 border-slate-300',
          line: 'bg-slate-100',
          label: 'text-slate-400'
        }
      case 'present':
        return {
          dot: 'bg-slate-600 border-slate-700',
          line: 'bg-slate-200',
          label: 'text-slate-700 font-normal'
        }
      case 'future':
        return {
          dot: 'bg-slate-400 border-slate-500',
          line: 'bg-slate-100',
          label: 'text-slate-600'
        }
      default:
        return {
          dot: 'bg-slate-200 border-slate-300',
          line: 'bg-slate-100',
          label: 'text-slate-400'
        }
    }
  }

  const styles = getPhaseStyles()

  return (
    <div className="flex gap-4">
      {/* 时间轴线 */}
      <div className="flex flex-col items-center">
        <div className={`w-2 h-2 rounded-full border ${styles.dot} flex-shrink-0`} />
        {!isActive && <div className={`w-px h-full ${styles.line} mt-2`} />}
      </div>

      {/* 内容区 */}
      <div className="flex-1 pb-8">
        {children}
      </div>
    </div>
  )
}

/**
 * 时空动态区组件
 */
function TemporalDynamicsSection({ temporal }) {
  if (!temporal) return null

  return (
    <div className="px-10 py-8 border-b border-slate-100">
      <h3 className="text-[10px] font-normal text-slate-500 mb-6 flex items-center gap-2 tracking-wide uppercase">
        <Clock className="w-3.5 h-3.5" strokeWidth={1.5} />
        时空演化
      </h3>

      <div className="space-y-0">
        {/* 过去 */}
        {temporal.past && (
          <TimelineNode phase="past">
            <div className="text-[10px] font-normal text-slate-400 mb-3 tracking-wide uppercase">过去</div>
            <p className="text-sm text-slate-600 leading-relaxed font-normal">
              {temporal.past.summary}
            </p>
          </TimelineNode>
        )}

        {/* 现在 */}
        {temporal.present && (
          <TimelineNode phase="present">
            <div className="text-[10px] font-normal text-slate-600 mb-3 tracking-wide uppercase">现在</div>
            <p className="text-sm text-slate-800 leading-relaxed font-normal">
              {temporal.present.summary}
            </p>
          </TimelineNode>
        )}

        {/* 未来 */}
        {temporal.future && (
          <TimelineNode phase="future" isActive>
            <div className="text-[10px] font-normal text-slate-600 mb-5 tracking-wide uppercase">未来</div>
            
            <div className="space-y-4">
              {/* Base Case */}
              {temporal.future.base_case && (
                <ScenarioCard scenario={temporal.future.base_case} type="base" />
              )}

              {/* Tail Risk */}
              {temporal.future.tail_risk && (
                <ScenarioCard scenario={temporal.future.tail_risk} type="risk" />
              )}
            </div>
          </TimelineNode>
        )}
      </div>
    </div>
  )
}

/**
 * 证据信源区组件
 */
function EvidenceSection({ evidence }) {
  if (!evidence) return null

  const getConfidenceColor = (score) => {
    if (score >= 0.8) return 'bg-slate-600'
    if (score >= 0.6) return 'bg-slate-500'
    return 'bg-slate-400'
  }

  return (
    <div className="px-10 py-8">
      <h3 className="text-[10px] font-normal text-slate-500 mb-6 tracking-wide uppercase">置信度与来源</h3>

      {/* AI 置信度 */}
      {evidence.confidence_score !== undefined && (
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={SPRING_CONFIG.card}
          className="mb-8"
        >
          <div className="flex items-baseline justify-between mb-4">
            <span className="text-sm font-normal text-slate-600">置信度</span>
            <span className="text-base font-mono text-slate-800 tabular-nums">
              {(evidence.confidence_score * 100).toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${evidence.confidence_score * 100}%` }}
              transition={{ 
                type: "spring",
                stiffness: 200,
                damping: 20,
                delay: 0.2
              }}
              className={`h-full ${getConfidenceColor(evidence.confidence_score)}`}
            />
          </div>
        </motion.div>
      )}

      {/* 新闻来源 */}
      {evidence.sources && evidence.sources.length > 0 && (
        <div>
          <div className="text-sm font-normal text-slate-600 mb-4">
            参考来源 <span className="font-mono text-slate-400 tabular-nums">({evidence.sources.length})</span>
          </div>
          <div className="space-y-3">
            {evidence.sources.slice(0, 5).map((source, idx) => (
              <motion.a
                key={idx}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                initial={{ x: -10, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ 
                  ...SPRING_CONFIG.card,
                  delay: idx * 0.05
                }}
                whileHover={{ x: 4 }}
                className="block p-5 bg-slate-50 hover:bg-slate-100 rounded-md group"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-normal text-slate-800 line-clamp-2 group-hover:text-slate-900 leading-relaxed mb-3">
                      {source.title}
                    </div>
                    {source.date && (
                      <div className="text-[10px] text-slate-500 font-mono">
                        {source.date}
                      </div>
                    )}
                  </div>
                  <ExternalLink className="w-4 h-4 text-slate-400 group-hover:text-slate-600 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                </div>
              </motion.a>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * 主组件 - NodeDetailDrawer
 */
function NodeDetailDrawer({ nodeData, isOpen, onClose }) {
  if (!isOpen || !nodeData) return null

  return (
    <div className="h-full overflow-y-auto">
      {/* Header */}
      <DrawerHeader meta={nodeData.meta} onClose={onClose} />

      {/* Topology */}
      <TopologySection topology={nodeData.topology} />

      {/* Temporal Dynamics */}
      <TemporalDynamicsSection temporal={nodeData.temporal_dynamics} />

      {/* Evidence */}
      <EvidenceSection evidence={nodeData.evidence} />
    </div>
  )
}

export default NodeDetailDrawer



