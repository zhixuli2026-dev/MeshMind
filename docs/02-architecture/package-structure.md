# Python 包内部结构

## 目录布局

```
src/meshmind/
├── __init__.py              # 公开 API：Workspace, KnowledgeGraph
│
├── api/                     # 接入层
│   ├── app.py               # FastAPI 实例 + 生命周期
│   ├── deps.py              # 依赖注入
│   ├── middleware.py         # JWT/API Key 解析
│   ├── routes/              # REST 路由
│   │   ├── workspaces.py / extract.py / nodes.py / search.py
│   │   ├── relations.py / documents.py / members.py / auth.py
│   └── sse/                 # SSE 端点
│       ├── agent.py / task.py
│
├── agents/                  # Agent 层
│   ├── main_agent.py        # MainAgent
│   ├── knowledge_agent.py   # KnowledgeAgent（LangGraph React Loop）
│   └── state.py             # AgentState
│
├── core/                    # 核心业务层
│   ├── config.py            # Settings
│   ├── workspace.py         # Workspace（公开 API）
│   ├── knowledge.py         # KnowledgeGraph（公开 API）
│   ├── extraction.py        # 知识提取管线
│   ├── graph.py             # 图谱 CRUD
│   ├── retrieval.py         # 知识检索
│   ├── lifecycle.py         # 活力值/半衰期
│   └── maintenance.py       # 入库维护
│
├── db/                      # 数据库层
│   ├── engine.py            # 连接管理
│   ├── models.py            # ORM 模型
│   └── repositories/        # Repository 类
│
├── llm/                     # LLM 基础设施
│   ├── harness.py           # LLMHarness
│   └── prompts.py           # Prompt 模板
│
├── mcp/                     # MCP Server
│   └── server.py
│
├── embedding/               # Embedding
│   └── encoder.py           # BGE-M3
│
└── storage/                 # 文件存储
    └── s3.py                # MinIO/S3
```

## 依赖方向

```
api → agents → core → {db, llm, embedding, storage}
api → core (search 等直连)
```
