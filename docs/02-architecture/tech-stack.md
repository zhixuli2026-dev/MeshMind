# 技术栈

## 后端

| 技术 | 用途 |
|------|------|
| **Python 3.12+** | 主要开发语言 |
| **FastAPI** | Web 框架，提供 REST API |
| **LangChain** | LLM 框架，统一多模型调用和 Agent 编排 |
| **PostgreSQL 16** | 主数据库（TimescaleDB + pgvector） |

### 数据库扩展

| 扩展 | 用途 |
|------|------|
| **TimescaleDB 2.26** | 时间序列，知识活力/半衰期的时间维度存储 |
| **pgvector 0.8** | 向量存储和相似度搜索 |

## 存储

| 技术 | 用途 |
|------|------|
| **MinIO** (开发) / **AWS S3** (生产) | 文档文件存储（Markdown，最大 30MB） |
| **PostgreSQL** | 元数据和知识图谱存储，S3 key 关联 |

## 前端

| 技术 | 用途 |
|------|------|
| **TypeScript** | 前端开发语言 |
| **Vite** | 构建工具 |
| **React** | UI 框架 |

两个独立前端应用：
- **Workbench**：管理员知识管理面板
- **Q&A 问答界面**：用户问答入口

## LLM

| 配置 | 值 |
|------|-----|
| Pro 模型（复杂任务） | `deepseek-v4-pro` |
| Flash 模型（简单任务） | `deepseek-v4-flash` |
| API 端点 | https://api.deepseek.com/anthropic |
| 编排框架 | LangChain |

## Embedding

| 配置 | 值 |
|------|-----|
| 模型 | BAAI/bge-m3 |
| 维度 | 1024 |
| 最大序列长度 | 8192 tokens |
| 部署方式 | 本地 GPU (RTX 3060 12GB) / sentence-transformers |
| 存储 | pgvector |
