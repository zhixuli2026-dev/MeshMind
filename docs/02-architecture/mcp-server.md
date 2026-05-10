# MCP Server 设计

## 定位

MeshMind Agent 通过 **MCP (Model Context Protocol)** 暴露为外部多 Agent 系统的知识工具。

外部 Agent 系统（如 Claude Code、自定义 Multi-Agent 框架）可以直接调用 MeshMind MCP Server，将 MeshMind 作为"知识查询 + 知识写入"的工具节点。

## MCP 设计

### 工具列表

| 工具名 | 功能 | 输入 | 输出 |
|--------|------|------|------|
| `search_knowledge` | 检索知识 | `query`, `workspace_id` | 相关知识点 + 溯源 |
| `extract_knowledge` | 从对话提取知识 | `messages[]`, `workspace_id`, `session_id`, `user_id` | 提取结果摘要 |
| `get_knowledge` | 获取单条知识 | `node_id`, `workspace_id` | 标题 + 摘要 + 文档 |
| `list_related` | 获取关联知识 | `node_id`, `workspace_id`, `relation_type?` | 关联知识点列表 |
| `add_document` | 上传文档提炼知识 | `content`, `title`, `workspace_id`, `user_id` | 提炼结果 |

### MCP Server 实现

作为 FastAPI 的一个子模块运行，共享同一个进程：

```
FastAPI App
  ├── /api/v1/*          REST API
  ├── /sse/*             SSE 端点
  └── /mcp               MCP Server (SSE transport)
```

使用 `mcp` Python 包实现，通过 SSE 传输协议与外部 MCP 客户端通信。

## 调用方式

外部 Agent 在 `.mcp.json` 或类似配置中注册：

```json
{
  "mcpServers": {
    "meshmind": {
      "url": "http://localhost:8000/mcp/sse"
    }
  }
}
```

外部 Agent 可以直接调用：

```
Agent: "我们的微服务数据库怎么选？"
  → 内部决策：需要查团队知识
  → 调用 meshmind.search_knowledge("微服务数据库选型")
  → MeshMind 返回相关知识点 + 溯源
  → Agent 基于 MeshMind 知识 + 自身推理回答
```

## 设计原则

- 工具粒度足够细，让外部 Agent 有充分的编排自由度
- 输入包含 `workspace_id`，保持租户隔离
- 返回结果包含溯源标记，外部 Agent 可以将 [N] 标记带回到最终回答中
- MCP Server 不暴露 Agent 的 React Loop 过程——这些是通过 SSE 给前端看的，MCP 调用是"工具化"的
