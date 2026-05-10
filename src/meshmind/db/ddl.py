"""Database initialization: create schema, types, tables, indexes."""

from sqlalchemy import text

from meshmind.db.engine import engine

INIT_SQL = """
CREATE SCHEMA IF NOT EXISTS meshmind;

-- Enums
DO $$ BEGIN
    CREATE TYPE meshmind.knowledge_type AS ENUM ('law', 'rule', 'best_practice', 'event');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE meshmind.relation_type AS ENUM (
        'prerequisite', 'complementary', 'derived_from', 'related_to', 'conflict'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- Extensions (should already exist, but ensure)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Workspaces
CREATE TABLE IF NOT EXISTS meshmind.workspaces (
    workspace_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name           TEXT NOT NULL,
    description    TEXT,
    api_key_hash   TEXT NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Knowledge Nodes
CREATE TABLE IF NOT EXISTS meshmind.knowledge_nodes (
    node_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES meshmind.workspaces(workspace_id),
    title           TEXT NOT NULL,
    summary         TEXT NOT NULL,
    knowledge_type  meshmind.knowledge_type NOT NULL,
    vitality        FLOAT NOT NULL DEFAULT 1.0,
    half_life       INTERVAL NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    embedding       vector(1024),
    source_type     TEXT NOT NULL,
    user_id         TEXT,
    session_id      TEXT,
    agent_id        TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_nodes_workspace ON meshmind.knowledge_nodes(workspace_id);
CREATE INDEX IF NOT EXISTS idx_nodes_type ON meshmind.knowledge_nodes(knowledge_type);
CREATE INDEX IF NOT EXISTS idx_nodes_active ON meshmind.knowledge_nodes(workspace_id, is_active);

-- Documents
CREATE TABLE IF NOT EXISTS meshmind.documents (
    document_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES meshmind.workspaces(workspace_id),
    title           TEXT NOT NULL,
    s3_key          TEXT NOT NULL,
    file_size       INTEGER NOT NULL,
    file_type       TEXT NOT NULL DEFAULT 'markdown',
    uploaded_by     TEXT,
    content_text    TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Node-Document link
CREATE TABLE IF NOT EXISTS meshmind.node_documents (
    node_id      UUID NOT NULL REFERENCES meshmind.knowledge_nodes(node_id),
    document_id  UUID NOT NULL REFERENCES meshmind.documents(document_id),
    PRIMARY KEY (node_id, document_id)
);

-- Relationships
CREATE TABLE IF NOT EXISTS meshmind.relationships (
    relationship_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES meshmind.workspaces(workspace_id),
    source_node_id  UUID NOT NULL REFERENCES meshmind.knowledge_nodes(node_id),
    target_node_id  UUID NOT NULL REFERENCES meshmind.knowledge_nodes(node_id),
    relation_type   meshmind.relation_type NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(source_node_id, target_node_id, relation_type)
);

CREATE INDEX IF NOT EXISTS idx_relations_source ON meshmind.relationships(source_node_id);
CREATE INDEX IF NOT EXISTS idx_relations_target ON meshmind.relationships(target_node_id);

-- Authors
CREATE TABLE IF NOT EXISTS meshmind.authors (
    author_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES meshmind.workspaces(workspace_id),
    user_id      TEXT NOT NULL,
    name         TEXT,
    UNIQUE(workspace_id, user_id)
);

-- Node-Author link
CREATE TABLE IF NOT EXISTS meshmind.node_authors (
    node_id    UUID NOT NULL REFERENCES meshmind.knowledge_nodes(node_id),
    author_id  UUID NOT NULL REFERENCES meshmind.authors(author_id),
    PRIMARY KEY (node_id, author_id)
);

-- Vitality Events (TimescaleDB hypertable)
CREATE TABLE IF NOT EXISTS meshmind.vitality_events (
    time         TIMESTAMPTZ NOT NULL DEFAULT now(),
    node_id      UUID NOT NULL,
    vitality     FLOAT NOT NULL,
    half_life    INTERVAL NOT NULL,
    event_type   TEXT NOT NULL,
    context      JSONB
);

SELECT create_hypertable('meshmind.vitality_events', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_vitality_node ON meshmind.vitality_events(node_id, time DESC);
"""


async def init_db():
    async with engine.begin() as conn:
        await conn.execute(text(INIT_SQL))
        # Create ivfflat index separately (needs data first, but can be created empty)
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_nodes_embedding "
            "ON meshmind.knowledge_nodes "
            "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
        ))


async def drop_schema():
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA IF EXISTS meshmind CASCADE"))
