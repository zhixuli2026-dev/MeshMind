# SSE 事件定义

SSE 用于向前端实时推送 Agent 工作过程和任务进度。

## Agent 工作流事件

### 连接

```
GET /workspaces/{ws_id}/sse/agent/{conversation_id}
```

### 事件类型

| 事件 | 触发时机 | 数据 |
|------|----------|------|
| `agent_start` | 会话开始 | `{"conversation_id": "...", "question": "..."}` |
| `main_agent_spawn` | Main Agent 生成子 Agent | `{"parent_id": "...", "agent_id": "...", "topic": "..."}` |
| `think` | Agent Think 阶段 | `{"agent_id": "...", "thought": "...", "missing": "..."}` |
| `act` | Agent Act 阶段 | `{"agent_id": "...", "action": "search", "target": "..."}` |
| `observe` | Agent Observe 阶段 | `{"agent_id": "...", "found_nodes": [...], "enough": true/false}` |
| `knowledge_loaded` | 渐进式加载 | `{"agent_id": "...", "node_id": "...", "level": "summary"/"document"}` |
| `source_linked` | 溯源引用 | `{"marker": "N1", "node_id": "...", "title": "..."}` |
| `agent_complete` | 子 Agent 完成 | `{"agent_id": "...", "summary": "..."}` |
| `answer_chunk` | 最终回答流式输出 | `{"text": "..."}` |
| `answer_complete` | 回答完成 | `{"full_text": "...", "sources": [{"N": 1, "title": "...", "node_id": "..."}]}` |
| `error` | 错误 | `{"agent_id": "...", "message": "..."}` |

## 提取任务事件

```
GET /workspaces/{ws_id}/sse/task/{任务ID}
```

| 事件 | 说明 |
|------|------|
| `task_progress` | `{"stage": "loading"/"extracting"/"linking"/"done", "progress": 0-100}` |
| `task_complete` | `{"created_nodes": [...], "updated_nodes": [...], "conflicts": [...]}` |
| `task_error` | `{"message": "..."}` |

## 前端消费

```typescript
const evtSource = new EventSource(`/api/v1/workspaces/${wsId}/sse/agent/${convId}`);

evtSource.addEventListener("think", (e) => {
    const data = JSON.parse(e.data);
    // 渲染 Agent 的思考过程
});

evtSource.addEventListener("source_linked", (e) => {
    const data = JSON.parse(e.data);
    // 添加溯源标记 [N]
});
```
