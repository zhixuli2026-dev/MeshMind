# Agent 架构

MeshMind 包含两类 Agent，通过层级式的 spawn 机制协作完成知识探索和问答。

## Agent 类型

### Main Agent（主 Agent）

- **唯一对接用户**的 Agent，负责处理用户问答的入口
- 不直接做深度知识探索，而是**编排和调度**
- 核心能力：
  - 理解用户问题，拆解为子课题
  - **Spawn** 子 Knowledge Agent 去研究特定课题
  - 收集各子 Agent 的返回结果
  - 进行**最终的知识整理**，形成完整回答
  - 将问答过程中产生的新知识回写到知识生命周期系统

### Knowledge Agent（知识 Agent）

- 被 Main Agent spawn 出来，负责**特定课题的知识探索**
- 通过 **React Loop**（Reasoning + Acting 循环）工作：
  - 从深度上索引知识：沿知识图谱向下钻取
  - 从广度上索引知识：沿关联关系横向扩展
  - 整理检索到的知识
  - 形成该课题的回答
- Knowledge Agent 之间可以**互相 spawn**：
  - 一个 Knowledge Agent 发现课题涉及多个子领域时
  - Spawn 新的 Knowledge Agent 去研究子课题
  - 父 Agent 收集子 Agent 结果进行合并

## 层级协作模型

```
用户
  ↕
Main Agent（唯一用户接口）
  ├── Spawn → Knowledge Agent A（研究课题 A）
  │            ├── React Loop：搜索 → 评估 → 扩展 → 整理
  │            └── Spawn → Knowledge Agent A1（子课题 A1）
  ├── Spawn → Knowledge Agent B（研究课题 B）
  │            └── React Loop：搜索 → 评估 → 扩展 → 整理
  └── 整理 A + B + A1 的结果 → 完整回答用户
```

## React Loop 的工作方式

Knowledge Agent 的 React Loop 是一个持续决策循环：

```
1. Think（思考）：当前掌握了哪些信息？还缺什么？
2. Act（行动）：调用知识检索（直接检索/间接加载/渐进式加载）
3. Observe（观察）：新获取的知识是否足够？
4. 判断：
   - 足够 → 进入整理阶段
   - 不足 → 继续循环，或 spawn 子 Agent 深入研究
```

## 与知识生命周期的关系

- Agent 通过检索层获取知识
- Agent 回答问题的过程产生新知识（对话提炼）
- 新知识回写到知识生命周期系统，纳入图谱
- 形成"使用 → 产生 → 维护"的闭环

## 前端可见性

Agent 的工作过程必须对用户**完全可见**，通过 SSE 实时推送：

- Main Agent 的 spawn 决策和子 Agent 列表
- 每个 Knowledge Agent 的 React Loop 状态（Think/Act/Observe）
- 知识检索的路径（深度扩展/广度扩展）
- 最终回答的知识溯源标记

## React Loop 实现方案

**已决策：基于 LangGraph StateGraph 自实现。**

### 选择理由

- `langgraph` 已在项目依赖中
- 原生支持 streaming（每个节点转换产生事件 → 映射为 SSE Think/Act/Observe）
- 支持 subgraph → 天然支持 Agent spawn 嵌套
- 完全可控的节点内逻辑，Pro/Flash 路由在节点内部自由切换
- 比 LangChain AgentExecutor 更透明，比 DeepAgents 更成熟

### 核心结构

```
StateGraph(AgentState)
  ├── think: LLM 分析当前信息，判断还缺什么 → Pro
  ├── act: 检索知识 / 加载文档 → Flash/Pro 混合
  ├── observe: 评估新获取的知识，判断是否足够 → Pro
  └── 条件边: 够 → END / 不够 → think
```

每个节点产生 state transition 事件 → SSE 推送到前端。
