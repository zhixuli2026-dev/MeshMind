# LangGraph 流式输出 → SSE 事件映射

## LangGraph 事件源

使用 `graph.astream_events()` 获取细粒度事件：

```python
async for event in graph.astream_events(initial_state, version="v2"):
    kind = event["event"]
    name = event["name"]
    data = event["data"]
```

## 映射规则

| LangGraph 事件 | 映射到 SSE | 触发条件 |
|---------------|-----------|----------|
| `on_chain_start` name=`think` | `think` | Agent 开始 Think |
| `on_chain_end` name=`think` | — | Think 完成（不推送） |
| `on_chain_start` name=`act` | `act` | Agent 开始行动 |
| `on_chain_end` name=`act` | — | Act 完成（不推送） |
| `on_chain_start` name=`observe` | `observe` | Agent 开始观察 |
| `on_chain_end` name=`observe` | `knowledge_loaded` | 有新知识加载时推送 |
| 节点内自定义 `dispatch_event` | `source_linked` | 溯源标记关联时推送 |
| `on_chain_end` 顶层 | `agent_complete` | 子 Agent 任务完成 |
| 自定义 `dispatch_event` | `answer_chunk` | 最终回答流式输出 |
| 自定义 `dispatch_event` | `answer_complete` | 回答完成 + 溯源列表 |

## 实现方式

LangGraph 节点内部通过自定义 event 发射机制：

```python
from langgraph.types import StreamWriter

async def think_node(state: AgentState, writer: StreamWriter) -> AgentState:
    thought = await harness.call(...)
    writer(("think", {"thought": thought.content}))  # 推送到 SSE
    return {**state, "current_thought": thought.content}
```

`StreamWriter` 的输出被 `astream_events` 捕获为 `on_custom_event`，映射为对应 SSE 事件。

## Spawn 事件

Main Agent spawn 子 Agent 时：

```python
# main_agent.py
subgraph = create_knowledge_agent(topic)
async for event in subgraph.astream_events(initial_state, version="v2"):
    if event["event"] == "on_chain_start" and event["name"] == "think":
        yield SSEMainAgentSpawn(agent_id=agent_id, topic=topic)  # 先发 spawn 事件
        yield map_event(event)  # 再发 think 事件
```

## 连接生命周期

```
SSE 连接建立
  → agent_start (conversation_id, question)
  → main_agent_spawn (agent_id, topic) × N
      → think → act → observe → knowledge_loaded → ... (循环)
      → agent_complete (agent_id, summary)
  → answer_chunk × N (流式)
  → answer_complete (全文 + sources)
连接关闭
```
