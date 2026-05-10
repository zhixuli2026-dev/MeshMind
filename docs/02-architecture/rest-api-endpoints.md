# REST API 端点设计

所有 API 路径前缀：`/api/v1`

认证：`Authorization: Bearer <api_key | jwt_token>`

---

## Workspace

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/workspaces` | 注册新 Workspace，返回 API Key（仅展示一次） |
| `GET` | `/workspaces/{ws_id}` | 获取 Workspace 信息 |
| `PUT` | `/workspaces/{ws_id}` | 更新 Workspace 配置（admin） |
| `GET` | `/workspaces/{ws_id}/stats` | 知识统计（总量、类型分布、活力分布） |

## 知识提取

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/workspaces/{ws_id}/extract/conversation` | 从对话提取知识（异步，返回 task_id） |
| `POST` | `/workspaces/{ws_id}/extract/document` | 上传 Markdown 文档提炼知识（异步） |
| `GET` | `/workspaces/{ws_id}/tasks/{task_id}` | 查询异步任务状态 |

### 请求体

```json
// POST /extract/conversation
{
    "messages": [
        {"role": "user", "content": "..."},
        {"role": "agent", "content": "..."}
    ],
    "user_id": "user-001",
    "session_id": "sess-001"
}

// POST /extract/document
{
    "content": "# 标题\n\n文档内容...",
    "title": "数据库使用规范",
    "user_id": "user-001"
}
```

## 知识点

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/workspaces/{ws_id}/nodes` | 手动创建知识点（知识卡片） |
| `GET` | `/workspaces/{ws_id}/nodes/{node_id}` | 获取知识点详情 |
| `PUT` | `/workspaces/{ws_id}/nodes/{node_id}` | 更新知识点 |
| `DELETE` | `/workspaces/{ws_id}/nodes/{node_id}` | 删除知识点（is_active=0） |
| `GET` | `/workspaces/{ws_id}/nodes/{node_id}/related` | 获取关联知识点 |
| `GET` | `/workspaces/{ws_id}/nodes/{node_id}/documents` | 渐进式加载关联文档 |

## 知识检索

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/workspaces/{ws_id}/search?q=微服务数据库&type=rule&limit=20` | 直接检索（向量 + BM25） |

## 关系

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/workspaces/{ws_id}/relations` | 创建知识点关系 |
| `DELETE` | `/workspaces/{ws_id}/relations/{rel_id}` | 删除关系 |

## 文档

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/workspaces/{ws_id}/documents` | 文档列表 |
| `GET` | `/workspaces/{ws_id}/documents/{doc_id}` | 文档详情 |
| `DELETE` | `/workspaces/{ws_id}/documents/{doc_id}` | 删除文档 |

## 成员管理

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/workspaces/{ws_id}/members` | 成员列表 |
| `POST` | `/workspaces/{ws_id}/members` | 添加成员（admin） |
| `DELETE` | `/workspaces/{ws_id}/members/{user_id}` | 移除成员（admin） |

## Auth

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/auth/login` | 用户登录，返回 JWT |
| `POST` | `/workspaces/{ws_id}/auth/regenerate-key` | 重新生成 API Key（admin） |

## SSE 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/workspaces/{ws_id}/sse/agent/{conversation_id}` | SSE 流，实时推送 Agent 工作过程 |
| `GET` | `/workspaces/{ws_id}/sse/task/{task_id}` | SSE 流，推送提取任务进度 |
