from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.documents import Document
from app.db.models.chunks import Chunk

router = APIRouter(prefix="/documents", tags=["documents"])


# -------------------------------------------------
# 1️⃣ LIST DOCUMENTS (JWT-SAFE)
# -------------------------------------------------
@router.get("/")
def list_documents(
    current_user: dict = Depends(get_current_user),
    search: str | None = None,
    db: Session = Depends(get_db)
):
    # ✅ user_id ONLY from JWT
    user_id = current_user["sub"]

    query = db.query(Document).filter(Document.user_id == user_id)

    if search:
        query = query.filter(Document.filename.ilike(f"%{search}%"))

    docs = query.order_by(Document.upload_time.desc()).all()

    results = []

    for d in docs:
        chunk_count = (
            db.query(func.count(Chunk.id))
            .filter(Chunk.document_id == d.id)
            .scalar()
        )

        results.append({
            "id": d.id,
            "file_name": d.filename,
            "file_type": d.file_type,
            "pages": d.page_count or 0,
            "chunks": chunk_count or 0,
            "status": d.extraction_status or "UNKNOWN",
            "created_at": d.upload_time
        })

    return results


# -------------------------------------------------
# 2️⃣ DELETE DOCUMENT (JWT-SAFE)
# -------------------------------------------------
@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user["sub"]

    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user_id
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(doc)
    db.commit()

    return {
        "status": "deleted",
        "document_id": document_id
    }


# -------------------------------------------------
# 3️⃣ REPROCESS DOCUMENT (JWT-SAFE)
# -------------------------------------------------
@router.post("/{document_id}/reprocess")
def reprocess_document(
    document_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user["sub"]

    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user_id
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.extraction_status = "PROCESSING"
    db.commit()

    return {
        "status": "reprocessing_started",
        "document_id": document_id
    }
