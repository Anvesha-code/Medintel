from pathlib import Path
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



def process_upload(file_bytes: bytes, filename: str) -> dict:
    # -------------------------------------------------
    # 1. Detect file type
    # -------------------------------------------------
    mime, ext = detect_file_type(filename, file_bytes)

    # -------------------------------------------------
    # 2. Extract raw content (multi-format)
    # -------------------------------------------------
    extraction = extract_text(file_bytes, filename, mime)
    text_blocks = extraction["text_blocks"]
    meta = extraction.get("meta", {})


    page_count = meta.get("page_count")
    sheet_count = meta.get("sheet_count")
    language = meta.get("language")

    # -------------------------------------------------
    # 3. Clean text blocks
    # -------------------------------------------------
    cleaned_blocks = clean_text_blocks(text_blocks)

    # -------------------------------------------------
    # 4. Chunking (structured + unstructured)
    # -------------------------------------------------
    chunks = []
    for block in cleaned_blocks:
        if block["structured"]:
            chunks.extend(
                chunk_table_text(
                    block["raw_text"],
                    headers=block.get("headers")
                )
            )
        else:
            chunks.extend(chunk_text(block["raw_text"]))

    # -------------------------------------------------
    # 5. Save document metadata FIRST (get document_id)
    # -------------------------------------------------
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO documents
        (filename, file_type, page_count, sheet_count, language, extraction_status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (filename, ext, page_count, sheet_count, language, "PROCESSING")
    )
    document_id = cur.lastrowid

    # -------------------------------------------------
    # 6. Generate embeddings (DAY 8 CORE STEP)
    # -------------------------------------------------
    embedding_service = EmbeddingService()

    records = embedding_service.generate_embeddings_with_metadata(
        chunks=chunks,
        doc_id=document_id,
        source_type=ext,
        structured_flag=False
    )
    # -------------------------------------------------
    # 6.5 Store embeddings in Qdrant (MISSING STEP)
    # -------------------------------------------------
    vector_store = VectorStore()
    vector_store.store(records)

    # -------------------------------------------------
    # 7. Save chunks in DB
    # -------------------------------------------------
    for idx, chunk in enumerate(chunks):
        cur.execute(
            """
            INSERT INTO chunks
            (document_id, chunk_index, chunk_text, source_type)
            VALUES (?, ?, ?, ?)
            """,
            (document_id, idx, chunk, cleaned_blocks[0]["source_type"])
        )

    # -------------------------------------------------
    # 8. Update document status
    # -------------------------------------------------
    cur.execute(
        "UPDATE documents SET extraction_status=? WHERE id=?",
        ("EMBEDDED", document_id)
    )

    conn.commit()
    conn.close()

    # -------------------------------------------------
    # 9. Save chunks locally (debug / temp)
    # -------------------------------------------------
    saved_paths = save_chunks_locally(
        chunks,
        prefix=Path(filename).stem
    )

    # -------------------------------------------------
    # 10. Final response
    # -------------------------------------------------
    return {
        "document_id": document_id,
        "filename": filename,
        "file_type": ext,
        "page_count": page_count,
        "sheet_count": sheet_count,
        "language": language,
        "num_blocks": len(cleaned_blocks),
        "num_chunks": len(chunks),
        "sample_chunk": chunks[0][:300] if chunks else "",
        "saved_chunks": saved_paths[:5],
        "status": "EMBEDDED"
    }
