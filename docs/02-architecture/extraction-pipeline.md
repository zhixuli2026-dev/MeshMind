# 知识提取管线

## 对话提取

```
messages[] + user_id + session_id
  → ExtractionAgent (Pro): 识别知识 + 判断类型
  → GraphConnectAgent (Pro): 向量检索候选 → LLM 判断关系 → 维护策略
  → 写入: nodes, authors, relations, vitality_events
```

## 文档提取

```
markdown + title + user_id
  → 存储 MinIO → documents INSERT
  → DocumentAnalysisAgent (Pro): 整篇/拆散决策 → 生成知识点
  → GraphConnectAgent (Pro): 同对话管线
  → 写入
```

## 核心类

```python
class ExtractionPipeline:
    def __init__(self, harness, graph, encoder): ...

    async def extract_from_conversation(
        self, messages: list[dict], user_id: str, session_id: str, workspace_id: str
    ) -> ExtractionResult: ...

    async def extract_from_document(
        self, content: str, title: str, user_id: str, workspace_id: str
    ) -> ExtractionResult: ...

@dataclass
class ExtractionResult:
    task_id: str
    status: Literal["processing", "done", "error"]
    created_nodes: list[str]    # node_id 列表
    updated_nodes: list[str]
    conflicts: list[tuple[str, str]]  # (node_a, node_b) 冲突对
```

## 异步执行

提取不阻塞调用方。API 层收到请求后立即返回 task_id，后台运行管线。完成后通过 SSE 推送结果。
