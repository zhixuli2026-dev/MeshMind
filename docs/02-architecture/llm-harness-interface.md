# LLM Harness 接口

## 定位

LLM 调用安全护栏。业务代码不感知模型路由、重试、超时逻辑。

## 核心类

```python
class LLMHarness:
    async def call(
        self,
        messages: list[dict],
        task: TaskType,
        workspace_id: str,
        *,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        response_schema: type | None = None,
        retries: int = 3,
    ) -> LLMResponse: ...

    async def call_structured[T](
        self,
        messages: list[dict],
        task: TaskType,
        workspace_id: str,
        output_model: type[T],
    ) -> T: ...
```

## TaskType → 模型路由

| TaskType | 模型 | 说明 |
|----------|------|------|
| `CONVERSATION_EXTRACTION` | Pro | 对话知识提炼 |
| `DOCUMENT_ANALYSIS` | Pro | 文档拆解 |
| `AGENT_THINK` | Pro | Agent Think 阶段 |
| `CONFLICT_JUDGMENT` | Pro | 冲突判断 |
| `MAINTENANCE_JUDGMENT` | Pro | 入库维护判断 |
| `FINAL_ANSWER` | Pro | 最终回答整理 |
| `SIMILARITY_FILTER` | Flash | 相似度筛除 |
| `SIMPLE_CLASSIFY` | Flash | 简单分类 |
| `RELATION_CONFIRM` | Flash | 关系确认 |

## 返回类型

```python
@dataclass
class LLMResponse:
    content: str
    model: str
    usage: Usage
    latency_ms: int

@dataclass
class Usage:
    prompt_tokens: int
    completion_tokens: int
```

## 容错

- 超时：默认 60s
- 重试：3 次，指数退避（1s → 2s → 4s）
- 失败后 fallback：如果 Pro 不可用 → 降级到 Flash（记录日志）
