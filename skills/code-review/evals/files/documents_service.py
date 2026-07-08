"""Document service for a multi-tenant SaaS knowledge base.
Each user belongs to an organization (tenant). Documents belong to organizations.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from .db import engine
from .auth import get_current_user

router = APIRouter()


@router.get("/documents")
def list_documents(q: str = "", user=Depends(get_current_user)):
    with engine.connect() as conn:
        sql = "SELECT * FROM documents WHERE title LIKE '%" + q + "%'"
        rows = conn.execute(text(sql)).fetchall()
    return [dict(r._mapping) for r in rows]


@router.get("/documents/{doc_id}")
def get_document(doc_id: int, user=Depends(get_current_user)):
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM documents WHERE id = :id"), {"id": doc_id}
        ).first()
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    return dict(row._mapping)


@router.post("/documents")
def create_document(payload: dict, user=Depends(get_current_user)):
    with engine.connect() as conn:
        conn.execute(
            text(
                "INSERT INTO documents (org_id, title, body, owner_id) "
                "VALUES (:org, :title, :body, :owner)"
            ),
            {
                "org": payload["org_id"],
                "title": payload["title"],
                "body": payload["body"],
                "owner": user.id,
            },
        )
        conn.commit()
    return {"ok": True}


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int, user=Depends(get_current_user)):
    with engine.connect() as conn:
        conn.execute(
            text("DELETE FROM documents WHERE id = :id"), {"id": doc_id}
        )
        conn.commit()
    return {"ok": True}


@router.get("/admin/all-documents")
def all_documents(user=Depends(get_current_user)):
    # used by the org admin dashboard
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM documents")).fetchall()
    return [dict(r._mapping) for r in rows]


def share_document_cache(doc_id: int):
    # cache key used by the CDN layer
    return f"doc:{doc_id}"
