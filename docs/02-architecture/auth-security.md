# 认证与安全架构

## 认证方案：API Key + JWT 混合

### API Key（Workspace 级别）

每个 Workspace 注册时自动生成一个 API Key：

- 用于 SDK / 外部 Agent 调用 MeshMind API
- 绑定到一个 Workspace，拥有该 Workspace 内的完整访问权限
- 在 HTTP Header 中传递：`Authorization: Bearer <api_key>`
- 可重置（regenerate），旧 Key 立即失效

### JWT（用户级别）

用于 Workbench 和问答界面的用户登录：

- 用户通过 Workspace 成员身份登录
- JWT 包含：`workspace_id`, `user_id`, `role`（admin/member）
- 过期时间：24 小时（可配置）
- 刷新机制：refresh token（可选，v1 可先不做）

### 为什么两个

- API Key 简单，适合机器间通信（SDK/MCP 场景）
- JWT 适合有登录态的前端交互（Workbench/问答界面）
- 两者都通过同一个 `Bearer` 头传递，后端统一验证

## 权限模型

| 角色 | 管理成员 | 写 Law | 写知识 | 读知识 | 管理配置 |
|------|---------|--------|--------|--------|---------|
| **admin** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **member** | ❌ | ❌ | ✅ | ✅ | ❌ |

- 只有 admin 可以写入 Law 类型知识
- 只有 admin 可以管理 Workspace 配置
- 成员可以自由读写其他类型知识

## 安全措施

### API 安全
- 所有 API 走 HTTPS（生产环境）
- API Key 和 JWT 在服务端校验
- 请求频率限制（Rate Limiting）

### 数据隔离
- 所有查询强制带 `workspace_id` 过滤
- 中间件从 JWT/API Key 解析 workspace_id，注入请求上下文
- 不允许跨 Workspace 查询

### 密钥管理
- API Key 存储为 bcrypt hash，生成后仅展示一次
- JWT Secret 通过环境变量配置
- `.env` 文件不在版本控制中
