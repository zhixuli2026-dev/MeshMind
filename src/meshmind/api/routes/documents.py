from uuid import UUID

from fastapi import APIRouter, HTTPException

from meshmind.db.engine import AsyncSessionFactory
from meshmind.db.repositories.documents import DocumentRepository

router = APIRouter(prefix="/workspaces/{workspace_id}/documents", tags=["documents"])


@router.get("")
async def list_documents(workspace_id: str):
    async with AsyncSessionFactory() as session:
        repo = DocumentRepository(session)
        docs = await repo.find_by_workspace(UUID(workspace_id))
        return {
            "documents": [
                {
                    "document_id": str(d.document_id),
                    "title": d.title,
                    "file_size": d.file_size,
                    "file_type": d.file_type,
                    "uploaded_by": d.uploaded_by,
                    "created_at": d.created_at.isoformat() if d.created_at else None,
                }
                for d in docs
            ]
        }


@router.get("/{document_id}")
async def get_document(workspace_id: str, document_id: str):
    async with AsyncSessionFactory() as session:
        repo = DocumentRepository(session)
        doc = await repo.get_by_id(UUID(document_id))
        if doc is None:
            raise HTTPException(status_code=404, detail="Document not found")
        return {
            "document_id": str(doc.document_id),
            "title": doc.title,
            "s3_key": doc.s3_key,
            "file_size": doc.file_size,
            "file_type": doc.file_type,
            "uploaded_by": doc.uploaded_by,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
        }


@router.delete("/{document_id}")
async def delete_document(workspace_id: str, document_id: str):
    async with AsyncSessionFactory() as session:
        repo = DocumentRepository(session)
        doc = await repo.get_by_id(UUID(document_id))
        if doc is None:
            raise HTTPException(status_code=404, detail="Document not found")
        await repo.delete(doc)
        await session.commit()
        return {"deleted": True}
