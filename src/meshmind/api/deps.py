from uuid import UUID

from fastapi import Request

from meshmind.embedding.encoder import EmbeddingEncoder
from meshmind.llm.harness import LLMHarness
from meshmind.storage.s3 import StorageClient

_harness: LLMHarness | None = None
_storage: StorageClient | None = None


def init_services():
    global _harness, _storage
    _harness = LLMHarness()
    _storage = StorageClient()


def get_harness() -> LLMHarness:
    assert _harness is not None, "Services not initialized"
    return _harness


def get_storage() -> StorageClient:
    assert _storage is not None, "Services not initialized"
    return _storage


def get_workspace_id(request: Request) -> UUID:
    ws_id = getattr(request.state, "workspace_id", None)
    if ws_id is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Not authenticated")
    return UUID(ws_id)
