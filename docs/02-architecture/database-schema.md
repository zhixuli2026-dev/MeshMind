# 数据库 Schema 设计

所有表建立在 `meshmind` schema 下。

## 核心表结构

### workspaces — 工作空间（租户）

```sql
CREATE TABLE meshmind.workspaces (
    workspace_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name           TEXT NOT NULL,
    description    TEXT,
    api_key_hash   TEXT NOT NULL,                               -- bcrypt hash of API Key
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### knowledge_nodes — 知识点（L1 标题 + L2 摘要）

```sql
CREATE TYPE meshmind.knowledge_type AS ENUM ('law', 'rule', 'best_practice', 'event');

CREATE TABLE meshmind.knowledge_nodes (
    node_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES meshmind.workspaces(workspace_id),
    title           TEXT NOT NULL,                              -- L1 标题
    summary         TEXT NOT NULL,                              -- L2 摘要
    knowledge_type  meshmind.knowledge_type NOT NULL,
    vitality        FLOAT NOT NULL DEFAULT 1.0,                 -- 活力值 (0~1)
    half_life       INTERVAL NOT NULL,                          -- 当前半衰期
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    embedding       vector(1024),                               -- pgvector 向量 (BGE-M3)

    -- 溯源
    source_type     TEXT NOT NULL,                              -- 'conversation' / 'document' / 'manual'
    user_id         TEXT,                                       -- 贡献知识的用户
    session_id      TEXT,                                       -- 产生知识的会话
    agent_id        TEXT,                                       -- 提取知识的 Agent

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_nodes_workspace ON meshmind.knowledge_nodes(workspace_id);
CREATE INDEX idx_nodes_type ON meshmind.knowledge_nodes(knowledge_type);
CREATE INDEX idx_nodes_active ON meshmind.knowledge_nodes(workspace_id, is_active);
CREATE INDEX idx_nodes_embedding ON meshmind.knowledge_nodes USING ivfflat (embedding vector_cosine_ops);
```

### documents — 知识文档（L3）

文档文件存储在 S3/MinIO 中，数据库仅存储元数据和 S3 Key。

```sql
CREATE TABLE meshmind.documents (
    document_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES meshmind.workspaces(workspace_id),
    title           TEXT NOT NULL,
    s3_key          TEXT NOT NULL,                              -- S3 存储路径
    file_size       INTEGER NOT NULL,                           -- 文件大小（字节）
    file_type       TEXT NOT NULL DEFAULT 'markdown',           -- 文件类型（仅支持 markdown）
    uploaded_by     TEXT,                                       -- 上传者 user_id
    content_text    TEXT,                                       -- 提取的纯文本（LLM 提炼用）
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

文档上传限制：
- 格式：仅 `.md` (Markdown)
- 大小：最大 30MB

### node_documents — 知识点与文档的多对多关联

```sql
CREATE TABLE meshmind.node_documents (
    node_id      UUID NOT NULL REFERENCES meshmind.knowledge_nodes(node_id),
    document_id  UUID NOT NULL REFERENCES meshmind.documents(document_id),
    PRIMARY KEY (node_id, document_id)
);
```

### relationships — 知识点之间的关系

```sql
CREATE TYPE meshmind.relation_type AS ENUM (
    'prerequisite',    -- 前置条件
    'complementary',   -- 互补
    'derived_from',    -- 派生
    'related_to',      -- 一般关联
    'conflict'         -- 冲突
);

CREATE TABLE meshmind.relationships (
    relationship_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES meshmind.workspaces(workspace_id),
    source_node_id  UUID NOT NULL REFERENCES meshmind.knowledge_nodes(node_id),
    target_node_id  UUID NOT NULL REFERENCES meshmind.knowledge_nodes(node_id),
    relation_type   meshmind.relation_type NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE(source_node_id, target_node_id, relation_type)
);

CREATE INDEX idx_relations_source ON meshmind.relationships(source_node_id);
CREATE INDEX idx_relations_target ON meshmind.relationships(target_node_id);
```

### authors — 知识作者/贡献者

```sql
CREATE TABLE meshmind.authors (
    author_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES meshmind.workspaces(workspace_id),
    user_id      TEXT NOT NULL,
    name         TEXT,
    UNIQUE(workspace_id, user_id)
);
```

### node_authors — 知识点与作者的关联

```sql
CREATE TABLE meshmind.node_authors (
    node_id    UUID NOT NULL REFERENCES meshmind.knowledge_nodes(node_id),
    author_id  UUID NOT NULL REFERENCES meshmind.authors(author_id),
    PRIMARY KEY (node_id, author_id)
);
```

### vitality_events — 活力值变化记录（TimescaleDB 时序表）

```sql
CREATE TABLE meshmind.vitality_events (
    time         TIMESTAMPTZ NOT NULL,
    node_id      UUID NOT NULL,
    vitality     FLOAT NOT NULL,
    half_life    INTERVAL NOT NULL,
    event_type   TEXT NOT NULL,     -- 'decay' / 'access' / 'positive_feedback' / 'negative_feedback' / 'manual'
    context      JSONB              -- 附加上下文（如会话 ID、触发原因等）
);

SELECT create_hypertable('meshmind.vitality_events', 'time');
CREATE INDEX idx_vitality_node ON meshmind.vitality_events(node_id, time DESC);
```

## 表关系一览

```
workspaces
  ├── knowledge_nodes ──┬── node_documents ── documents
  │                     └── node_authors ── authors
  ├── relationships (source/target → knowledge_nodes)
  ├── documents
  ├── authors
  └── vitality_events (时序)
```
