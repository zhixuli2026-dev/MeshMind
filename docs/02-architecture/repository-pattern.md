# Repository 接口规范

所有数据访问通过 Repository 类，不直接写 SQL。

## 基类

```python
class BaseRepository[T]:
    model: type[T]  # SQLAlchemy model

    async def get_by_id(self, id: UUID) -> T | None: ...
    async def list_all(self, *, limit: int = 100, offset: int = 0) -> list[T]: ...
    async def create(self, **kwargs) -> T: ...
    async def update(self, entity: T, **kwargs) -> T: ...
    async def delete(self, entity: T) -> None: ...  # soft delete
```

## 具体 Repository

### WorkspaceRepository
```python
class WorkspaceRepository(BaseRepository[WorkspaceModel]):
    async def get_by_api_key_hash(self, key_hash: str) -> WorkspaceModel | None: ...
```

### NodeRepository
```python
class NodeRepository(BaseRepository[KnowledgeNodeModel]):
    async def find_by_workspace(self, workspace_id: UUID, *,
        is_active: bool = True, limit: int = 100) -> list[KnowledgeNodeModel]: ...
    async def search_by_embedding(self, embedding: list[float], workspace_id: UUID,
        limit: int = 20) -> list[tuple[KnowledgeNodeModel, float]]: ...  # (node, cosine_distance)
    async def search_by_text(self, query: str, workspace_id: UUID,
        limit: int = 20) -> list[KnowledgeNodeModel]: ...  # BM25 via pg full-text search
    async def get_with_relations(self, node_id: UUID) -> KnowledgeNodeModel | None: ...
    async def get_authors(self, node_id: UUID) -> list[AuthorModel]: ...
    async def batch_get(self, node_ids: list[UUID]) -> list[KnowledgeNodeModel]: ...
```

### DocumentRepository
```python
class DocumentRepository(BaseRepository[DocumentModel]):
    async def find_by_workspace(self, workspace_id: UUID) -> list[DocumentModel]: ...
    async def get_documents_for_node(self, node_id: UUID) -> list[DocumentModel]: ...
```

### RelationRepository
```python
class RelationRepository(BaseRepository[RelationModel]):
    async def find_by_source(self, node_id: UUID) -> list[RelationModel]: ...
    async def find_by_target(self, node_id: UUID) -> list[RelationModel]: ...
    async def find_between(self, node_a: UUID, node_b: UUID) -> RelationModel | None: ...
    async def find_conflicts(self, workspace_id: UUID) -> list[RelationModel]: ...
```

### VitalityRepository
```python
class VitalityRepository:
    async def get_latest_event(self, node_id: UUID) -> VitalityEvent | None: ...
    async def record_event(self, node_id: UUID, vitality: float,
        half_life: timedelta, event_type: str) -> VitalityEvent: ...
```

### AuthorRepository
```python
class AuthorRepository(BaseRepository[AuthorModel]):
    async def get_or_create(self, workspace_id: UUID, user_id: str, name: str = None) -> AuthorModel: ...
    async def get_authors_for_node(self, node_id: UUID) -> list[AuthorModel]: ...
```
