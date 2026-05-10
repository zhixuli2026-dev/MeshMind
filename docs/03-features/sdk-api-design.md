# SDK API 设计

## 安装

```bash
pip install meshmind
```

## 初始化

```python
from meshmind import Workspace, KnowledgeGraph

# 连接已有 Workspace
ws = Workspace.connect(api_key="msm_xxx")

# 或者注册新 Workspace
ws = Workspace.create(name="后端团队", description="后端技术规范与最佳实践")
```

## 核心类

### Workspace

```python
ws = Workspace.connect(api_key="msm_xxx")

# 获取知识图谱操作接口
kg = ws.knowledge_graph()

# 获取当前状态概览
stats = ws.stats()  # {"node_count": 150, "type_distribution": {...}}
```

### KnowledgeGraph — 知识写入

```python
# 从对话提取知识（非阻塞，异步完成）
result = kg.extract_from_conversation(
    messages=[
        {"role": "user", "content": "我们的微服务数据库怎么选？"},
        {"role": "agent", "content": "根据团队规范，每个微服务应有独立 DB 实例..."}
    ],
    user_id="user-001",
    session_id="sess-2024-001"
)
# 返回: {"task_id": "ext-xxx", "status": "processing"}

# 从文档提炼知识
result = kg.extract_from_document(
    content="# 数据库规范\n\n## 实例管理\n每个微服务应有独立的数据库实例...",
    title="数据库使用规范",
    user_id="user-001"
)

# 手动写入知识卡片
node = kg.add_knowledge(
    title="微服务独立数据库实例",
    summary="每个微服务应使用独立的数据库实例以确保数据隔离。",
    knowledge_type="rule",
    user_id="user-001",
    document_ids=None  # 可选，关联已有文档
)
```

### KnowledgeGraph — 知识检索

```python
# 直接检索
results = kg.search("微服务数据库选型")
# [{"node_id": "...", "title": "...", "summary": "...", "score": 0.92, "sources": [...]}, ...]

# 获取单条知识
node = kg.get(node_id="node-xxx")

# 获取关联知识
related = kg.get_related(node_id="node-xxx", relation_type="complementary")

# 渐进式加载（从摘要获取关联文档）
docs = kg.load_documents(node_id="node-xxx")
```

### KnowledgeGraph — 知识维护

```python
# 删除知识
kg.delete(node_id="node-xxx")

# 创建关系
kg.create_relation(
    source="node-A",
    target="node-B", 
    relation_type="prerequisite"
)

# 解决冲突
kg.resolve_conflict(node_id="node-X", action="dismiss")
```

## 返回格式

所有检索结果包含溯源信息：

```python
{
    "node_id": "uuid",
    "title": "微服务独立数据库实例",
    "summary": "每个微服务应使用独立的数据库实例...",
    "knowledge_type": "rule",
    "vitality": 0.85,
    "sources": [
        {"source_type": "document", "title": "数据库使用规范", "user_id": "user-001"},
        {"source_type": "conversation", "session_id": "sess-001", "user_id": "user-002"}
    ],
    "relations": [
        {"target": "node-B", "type": "complementary"}
    ]
}
```

## 异步模型

知识提取操作不阻塞：

- `extract_from_conversation()` / `extract_from_document()` 立即返回 `task_id`
- LLM 提取在后台异步完成
- 可通过 `ws.get_task(task_id)` 查询状态
- 完成后结果自动写入知识图谱
