# 前端重构说明 - Perplexity 风格动态布局

## 重构概览

已将传统的固定布局重构为 **Perplexity 风格的动态三阶段布局**，提供更流畅的用户体验。

---

## 核心状态变量

```javascript
const [hasAnalyzed, setHasAnalyzed] = useState(false)
```

**作用**：控制整个页面的布局模式切换

**触发时机**：
- 用户点击"开始分析"按钮时，`setHasAnalyzed(true)`
- 布局从居中输入框 → 三栏工作台

---

## 三个阶段详解

### Phase 1: 初始状态 (hasAnalyzed === false)

**布局特征**：
```jsx
<div className="h-screen w-screen flex flex-col items-center justify-center">
```

**视觉效果**：
- ✅ 全屏居中
- ✅ 渐变背景 (`bg-gradient-to-br from-slate-50 via-slate-100 to-slate-50`)
- ✅ 大标题 "CausalFlow"
- ✅ 居中输入表单 (`max-w-2xl w-full`)
- ✅ 底部提示文字

**用户体验**：
- 类似 Perplexity / ChatGPT 的首页
- 聚焦于输入，无干扰
- 简洁优雅

---

### Phase 2: 分析状态 (hasAnalyzed === true)

**布局特征**：
```jsx
<div className="h-screen w-screen flex overflow-hidden">
```

**三栏结构**：

#### 1. Left Sidebar (输入区)
```jsx
<div className="w-[320px] h-full border-r border-slate-200 bg-white overflow-y-auto flex-shrink-0">
```

**内容**：
- 品牌标题 (CausalFlow)
- 输入表单 (QueryPanel)
- 可滚动

**宽度**：固定 320px

---

#### 2. Center Stage (无限画布)
```jsx
<div className="flex-1 h-full relative bg-slate-50">
```

**内容**：
- React Flow 图谱
- 加载动画
- 空状态提示

**宽度**：`flex-1` (占据所有剩余空间)

**特点**：
- 霸占中间所有空间
- 无滚动条（图谱自带缩放/拖拽）
- 相对定位，方便叠加元素

---

#### 3. Right Sidebar (分析说明)
```jsx
<div className="w-[380px] h-full border-l border-slate-200 bg-white overflow-y-auto flex-shrink-0">
```

**内容**：
- 分析说明文字
- 图谱统计信息（节点数、边数、数据源数）
- 可滚动

**宽度**：固定 380px

---

### Phase 3: 悬浮数据源 (FAB + Popover)

#### FAB 按钮
```jsx
<button className="fixed bottom-8 right-8 z-50 ... bg-slate-900 text-white rounded-full">
```

**位置**：右下角固定  
**样式**：圆角胶囊按钮  
**内容**：`🔗 引用来源 (12)`  
**交互**：点击展开 Popover

---

#### Popover 面板
```jsx
<div className="fixed bottom-24 right-8 z-50 w-[480px] max-h-[60vh] ... shadow-2xl">
```

**特性**：
- ✅ 从 FAB 上方弹出
- ✅ 最大高度 60vh，内容可滚动
- ✅ 遮罩层背景 (`bg-black bg-opacity-20`)
- ✅ 点击遮罩关闭
- ✅ 列表展示所有数据源

**数据源卡片**：
- 序号标记
- 来源节点名称
- 新闻标题
- 域名 + 链接

---

## 关键改进

### 1. 移除的组件
- ❌ `DataSourcesPanel.jsx` - 不再使用底部固定面板
- ❌ 顶部 Header - 简化为侧边栏标题

### 2. 布局优势

**Before (旧版)**：
```
┌─────────────────────────────┐
│         Header              │
├──────┬──────────────────────┤
│ Left │      Center          │
│ Side │      Graph           │
│ bar  │                      │
└──────┴──────────────────────┘
│   Bottom Data Sources       │
└─────────────────────────────┘
```

**After (新版)**：
```
┌──────┬──────────────┬───────┐
│ Left │   Center     │ Right │
│ 320px│   flex-1     │ 380px │
│      │              │       │
│ Input│    Graph     │ Info  │
│      │              │       │
│      │              │       │
└──────┴──────────────┴───────┘
                    [FAB] 🔗
```

**优势**：
- ✅ 图谱占据最大空间
- ✅ 无底部遮挡
- ✅ 数据源按需展开
- ✅ 三栏信息密度合理

---

## 状态流转图

```
用户访问
   ↓
[Phase 1] 居中输入框
   ↓ (点击"开始分析")
setHasAnalyzed(true)
   ↓
[Phase 2] 三栏布局展开
   ↓ (loading = true)
显示加载动画
   ↓ (数据返回)
渲染图谱 + 说明
   ↓ (有数据源)
[Phase 3] 显示 FAB
   ↓ (点击 FAB)
弹出 Popover
```

---

## 响应式考虑

当前实现为**桌面优先**，建议后续添加：

```jsx
// 移动端检测
const isMobile = window.innerWidth < 768

// 移动端布局调整
{isMobile ? (
  <MobileLayout />
) : (
  <DesktopLayout />
)}
```

---

## 动画建议（可选）

### 1. 布局切换动画
```jsx
// 使用 Framer Motion
import { motion } from 'framer-motion'

<motion.div
  initial={{ opacity: 0, scale: 0.95 }}
  animate={{ opacity: 1, scale: 1 }}
  transition={{ duration: 0.3 }}
>
  {/* 三栏布局 */}
</motion.div>
```

### 2. FAB 入场动画
```jsx
<motion.button
  initial={{ scale: 0, opacity: 0 }}
  animate={{ scale: 1, opacity: 1 }}
  transition={{ delay: 0.5, type: "spring" }}
>
  引用来源
</motion.button>
```

### 3. Popover 弹出动画
```jsx
<motion.div
  initial={{ y: 20, opacity: 0 }}
  animate={{ y: 0, opacity: 1 }}
  exit={{ y: 20, opacity: 0 }}
>
  {/* Popover 内容 */}
</motion.div>
```

---

## 测试清单

- [ ] 首次访问显示居中输入框
- [ ] 点击"开始分析"触发布局切换
- [ ] 三栏布局正确渲染
- [ ] 图谱占据中间所有空间
- [ ] 左右侧边栏可独立滚动
- [ ] FAB 按钮显示正确的数据源数量
- [ ] 点击 FAB 弹出 Popover
- [ ] 点击遮罩关闭 Popover
- [ ] 数据源链接可点击跳转

---

## 文件清单

**已修改**：
- ✅ `frontend/src/App.jsx` - 主布局重构

**可删除**（已不使用）：
- ⚠️ `frontend/src/components/DataSourcesPanel.jsx` - 可选删除

**未修改**（继续使用）：
- ✅ `frontend/src/components/QueryPanel.jsx`
- ✅ `frontend/src/components/CausalGraph.jsx`
- ✅ `frontend/src/components/CustomNode.jsx`

---

## 下一步优化建议

### 1. 添加"返回首页"按钮
```jsx
<button onClick={() => setHasAnalyzed(false)}>
  ← 返回首页
</button>
```

### 2. 保存历史查询
```jsx
const [history, setHistory] = useState([])

// 每次分析后保存
setHistory([...history, { query, timestamp, graphData }])
```

### 3. 导出图谱功能
```jsx
<button onClick={exportGraph}>
  导出 PNG
</button>
```

### 4. 键盘快捷键
```jsx
// Cmd/Ctrl + K 聚焦输入框
// Esc 关闭 Popover
```

---

## 性能优化

### 1. 懒加载图谱组件
```jsx
const CausalGraph = lazy(() => import('./components/CausalGraph'))
```

### 2. 数据源虚拟滚动
```jsx
// 使用 react-window 优化长列表
import { FixedSizeList } from 'react-window'
```

### 3. 防抖搜索
```jsx
const debouncedAnalyze = useMemo(
  () => debounce(handleAnalyze, 500),
  []
)
```

---

生成时间: 2026-02-19 21:45  
重构版本: 2.0 (Perplexity Style)

