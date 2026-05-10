# 异步任务管理

## 方案：内存任务队列 + asyncio.create_task

不引入 Celery/Redis。v1 阶段用 in-memory task registry。

## 核心类

```python
@dataclass
class TaskInfo:
    task_id: str          # UUID
    status: Literal["pending", "running", "done", "error"]
    progress: float       # 0-100
    result: dict | None
    error: str | None
    created_at: float
    updated_at: float

class TaskManager:
    _tasks: dict[str, TaskInfo] = {}

    def create(self) -> TaskInfo: ...
    def get(self, task_id: str) -> TaskInfo | None: ...
    def update(self, task_id: str, **kwargs): ...

    async def run(self, coro, task_id: str): ...
```

## 使用方式

```python
task_manager = TaskManager()

# API 层
@router.post("/extract/conversation")
async def extract_conversation(body: ExtractRequest):
    task = task_manager.create()
    asyncio.create_task(
        task_manager.run(pipeline.extract(body), task.task_id)
    )
    return {"task_id": task.task_id}

# 状态查询
@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    return task_manager.get(task_id)
```

## 限制

- 进程重启丢失未完成任务（v1 可接受，提取是不阻塞的异步操作）
- 后续可升级为持久化队列（PG 表或 Redis）
