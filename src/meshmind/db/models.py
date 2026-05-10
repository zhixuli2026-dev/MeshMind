import uuid
from datetime import datetime, timedelta

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Interval,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from meshmind.db.engine import Base

# ── Enums ────────────────────────────────────────────────────────────

knowledge_type_enum = Enum(
    "law", "rule", "best_practice", "event",
    name="knowledge_type", schema="meshmind", create_type=False,
)

relation_type_enum = Enum(
    "prerequisite", "complementary", "derived_from", "related_to", "conflict",
    name="relation_type", schema="meshmind", create_type=False,
)

# ── Workspace ────────────────────────────────────────────────────────

class WorkspaceModel(Base):
    __tablename__ = "workspaces"
    __table_args__ = {"schema": "meshmind"}

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    api_key_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()")
    )

# ── Knowledge Node ───────────────────────────────────────────────────

class KnowledgeNodeModel(Base):
    __tablename__ = "knowledge_nodes"
    __table_args__ = (
        Index("idx_nodes_workspace", "workspace_id"),
        Index("idx_nodes_type", "knowledge_type"),
        Index("idx_nodes_active", "workspace_id", "is_active"),
        {"schema": "meshmind"},
    )

    node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meshmind.workspaces.workspace_id"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    knowledge_type: Mapped[str] = mapped_column(knowledge_type_enum, nullable=False)
    vitality: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    half_life: Mapped[timedelta] = mapped_column(Interval, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    embedding = mapped_column(Vector(1024))

    source_type: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[str | None] = mapped_column(Text)
    session_id: Mapped[str | None] = mapped_column(Text)
    agent_id: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()")
    )

# ── Document ─────────────────────────────────────────────────────────

class DocumentModel(Base):
    __tablename__ = "documents"
    __table_args__ = {"schema": "meshmind"}

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meshmind.workspaces.workspace_id"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    s3_key: Mapped[str] = mapped_column(Text, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_type: Mapped[str] = mapped_column(Text, nullable=False, default="markdown")
    uploaded_by: Mapped[str | None] = mapped_column(Text)
    content_text: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

# ── Node-Document link ───────────────────────────────────────────────

class NodeDocumentModel(Base):
    __tablename__ = "node_documents"
    __table_args__ = {"schema": "meshmind"}

    node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meshmind.knowledge_nodes.node_id"),
        primary_key=True,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meshmind.documents.document_id"),
        primary_key=True,
    )

# ── Relationship ─────────────────────────────────────────────────────

class RelationModel(Base):
    __tablename__ = "relationships"
    __table_args__ = (
        UniqueConstraint("source_node_id", "target_node_id", "relation_type"),
        Index("idx_relations_source", "source_node_id"),
        Index("idx_relations_target", "target_node_id"),
        {"schema": "meshmind"},
    )

    relationship_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meshmind.workspaces.workspace_id"), nullable=False
    )
    source_node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meshmind.knowledge_nodes.node_id"), nullable=False
    )
    target_node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meshmind.knowledge_nodes.node_id"), nullable=False
    )
    relation_type: Mapped[str] = mapped_column(relation_type_enum, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

# ── Author ───────────────────────────────────────────────────────────

class AuthorModel(Base):
    __tablename__ = "authors"
    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id"),
        {"schema": "meshmind"},
    )

    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meshmind.workspaces.workspace_id"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str | None] = mapped_column(Text)

# ── Node-Author link ─────────────────────────────────────────────────

class NodeAuthorModel(Base):
    __tablename__ = "node_authors"
    __table_args__ = {"schema": "meshmind"}

    node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meshmind.knowledge_nodes.node_id"),
        primary_key=True,
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meshmind.authors.author_id"),
        primary_key=True,
    )

# ── Vitality Event ───────────────────────────────────────────────────

class VitalityEventModel(Base):
    __tablename__ = "vitality_events"
    __table_args__ = {"schema": "meshmind"}

    time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True, server_default=text("now()")
    )
    node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    vitality: Mapped[float] = mapped_column(Float, nullable=False)
    half_life: Mapped[timedelta] = mapped_column(Interval, nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[dict | None] = mapped_column(JSON)
