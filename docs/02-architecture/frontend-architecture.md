# 前端架构

## 项目结构

```
frontend/
├── packages/
│   ├── shared/              # 共用包
│   │   ├── design-system/   # Apple-style 组件库 + 主题
│   │   ├── api-client/      # TypeScript API 客户端
│   │   └── sse-client/      # SSE 事件订阅
│   │
│   ├── qa/                  # 问答界面
│   │   └── src/
│   │       ├── pages/ChatPage.tsx
│   │       ├── components/
│   │       │   ├── ChatPanel.tsx          # 对话区
│   │       │   ├── AgentTree.tsx          # Spawn 树
│   │       │   ├── ReactLoopTimeline.tsx  # Think→Act→Observe
│   │       │   └── SourcePanel.tsx        # 溯源侧边栏
│   │       └── hooks/useAgentSSE.ts
│   │
│   └── workbench/           # 管理面板
│       └── src/
│           ├── pages/ (Dashboard/Knowledge/Documents/Analysis/Members/Settings)
│           └── components/
│               ├── GraphView.tsx           # 知识图谱可视化 ⚠️ 重点关注
│               ├── NodeEditor.tsx
│               ├── DocumentUploader.tsx
│               └── VitalityChart.tsx
│
└── package.json
```

## 技术选择

| 层 | 选择 |
|----|------|
| 框架 | React + TypeScript |
| 构建 | Vite |
| 路由 | React Router |
| 状态 | React Context + useReducer |
| 样式 | Tailwind CSS |
| 图谱可视化 | 待定（Sigma.js / Cytoscape.js / D3 Canvas） |
| 时序图表 | Recharts |

## 图谱可视化要求

知识图谱展示需达到 Apple-style 的丝滑体验：
- Canvas/WebGL 渲染，避免 SVG 在大节点数时卡顿
- 力导向布局，过渡动画自然
- 缩放/拖拽流畅
- 节点按类型区分颜色和大小
- 关系边按类型区分线型和粗细
- 选中节点高亮关联边，其余淡出
