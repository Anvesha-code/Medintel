from pathlib import Path
from fastapi import HTTPException
from app.services.embeddings import EmbeddingService
from app.utils.file_type import detect_file_type
from app.services.extraction_dispatcher import extract_text
from app.services.text_processing import (
    clean_text_blocks,
    chunk_text,
    chunk_table_text,
    save_chunks_locally
)
from app.db.db import get_connection
from app.services.vector_store import VectorStore


def process_upload(file_bytes: bytes, filename: str, user_id: int) -> dict:

    # --------------------------------------------------
    # 1. Detect file type
    # --------------------------------------------------
    mime, ext = detect_file_type(filename, file_bytes)

    # --------------------------------------------------
    # 2. Extract content (SAFE)
    # --------------------------------------------------
    extraction = extract_text(file_bytes, filename, mime)

    if not extraction or "text_blocks" not in extraction:
        raise HTTPException(
            status_code=400,
            detail="Text extraction failed or unsupported document"
        )

    text_blocks = extraction["text_blocks"]
    meta = extraction.get("meta", {})

    page_count = meta.get("page_count")
    sheet_count = meta.get("sheet_count")
    language = meta.get("language")

    # --------------------------------------------------
    # 3. Clean text blocks
    # --------------------------------------------------
    cleaned_blocks = clean_text_blocks(text_blocks)

    if not cleaned_blocks:
        raise HTTPException(
            status_code=400,
            detail="No readable text found in document"
        )

    # --------------------------------------------------
    # 4. Chunking
    # --------------------------------------------------
    chunks_with_type = []

    for block in cleaned_blocks:
        source_type = "table" if block.get("structured") else "text"
        raw_text = block.get("raw_text", "")

        if not raw_text.strip():
            continue

        if source_type == "table":
            for c in chunk_table_text(raw_text):
                chunks_with_type.append({
                    "text": c,
                    "source_type": source_type
                })
        else:
            for c in chunk_text(raw_text):
                chunks_with_type.append({
                    "text": c,
                    "source_type": source_type
                })

    if not chunks_with_type:
        raise HTTPException(
            status_code=400,
            detail="Chunking failed – no chunks generated"
        )

    # --------------------------------------------------
    # 5. Save document metadata (WITH user_id)
    # --------------------------------------------------
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO documents
            (user_id, filename, file_type, page_count, sheet_count, language, extraction_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, filename, ext, page_count, sheet_count, language, "PROCESSING")
        )
        document_id = cur.lastrowid

        # --------------------------------------------------
        # 6. Generate embeddings
        # --------------------------------------------------
        embedding_service = EmbeddingService()

        records = embedding_service.generate_embeddings_with_metadata(
            chunks=chunks_with_type,
            doc_id=document_id,
            user_id=user_id
        )

        if not records:
            raise HTTPException(
                status_code=500,
                detail="Embedding generation failed"
            )

        # --------------------------------------------------
        # 7. Store embeddings in Qdrant
        # --------------------------------------------------
        vector_store = VectorStore()
        vector_store.store(records)

        # --------------------------------------------------
        # 8. Save chunks in DB
        # --------------------------------------------------
        for idx, chunk_obj in enumerate(chunks_with_type):
            cur.execute(
                """
                INSERT INTO chunks
                (document_id, user_id, chunk_index, chunk_text, source_type)
                VALUES (?, ?, ?, ?, ?)
                """,
                (document_id, user_id, idx, chunk_obj["text"], chunk_obj["source_type"])
            )

        # --------------------------------------------------
        # 9. Update document status
        # --------------------------------------------------
        cur.execute(
            "UPDATE documents SET extraction_status=? WHERE id=?",
            ("EMBEDDED", document_id)
        )

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )

    finally:
        conn.close()

    # --------------------------------------------------
    # 10. Save chunks locally (SAFE)
    # --------------------------------------------------
    saved_paths = save_chunks_locally(
        [c["text"] for c in chunks_with_type],
        prefix=f"{user_id}_{Path(filename).stem}"
    )

    # --------------------------------------------------
    # 11. Final response
    # --------------------------------------------------
    return {
        "document_id": document_id,
        "user_id": user_id,
        "filename": filename,
        "file_type": ext,
        "page_count": page_count,
        "sheet_count": sheet_count,
        "language": language,
        "num_blocks": len(cleaned_blocks),
        "num_chunks": len(chunks_with_type),
        "sample_chunk": chunks_with_type[0]["text"][:300],
        "saved_chunks": saved_paths[:5],
        "status": "EMBEDDED"
    }
