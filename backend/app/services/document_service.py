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

    # 1. Detect file type
    mime, ext = detect_file_type(filename, file_bytes)

    # 2. Extract raw content
    extraction = extract_text(file_bytes, filename, mime)
    text_blocks = extraction["text_blocks"]
    meta = extraction.get("meta", {})

    page_count = meta.get("page_count")
    sheet_count = meta.get("sheet_count")
    language = meta.get("language")

    # 3. Clean text blocks
    cleaned_blocks = clean_text_blocks(text_blocks)

    # 4. Chunking WITH source_type
    chunks_with_type = []

    for block in cleaned_blocks:
        source_type = "table" if block["structured"] else "text"

        if block["structured"]:
            for c in chunk_table_text(block["raw_text"]):
                chunks_with_type.append({
                    "text": c,
                    "source_type": source_type
                })
        else:
            for c in chunk_text(block["raw_text"]):
                chunks_with_type.append({
                    "text": c,
                    "source_type": source_type
                })

    # 5. Save document metadata
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

    # 6. Generate embeddings
    embedding_service = EmbeddingService()

    records = embedding_service.generate_embeddings_with_metadata(
        chunks=chunks_with_type,
        doc_id=document_id,
        user_id="test_user"
    )

    # 6.5 Store embeddings in Qdrant
    vector_store = VectorStore()
    vector_store.store(records)

    # 7. Save chunks in DB (optional but fixed)
    for idx, chunk_obj in enumerate(chunks_with_type):
        cur.execute(
            """
            INSERT INTO chunks
            (document_id, chunk_index, chunk_text, source_type)
            VALUES (?, ?, ?, ?)
            """,
            (document_id, idx, chunk_obj["text"], chunk_obj["source_type"])
        )

    # 8. Update document status
    cur.execute(
        "UPDATE documents SET extraction_status=? WHERE id=?",
        ("EMBEDDED", document_id)
    )

    conn.commit()
    conn.close()

    # 9. Save chunks locally
    saved_paths = save_chunks_locally(
        [c["text"] for c in chunks_with_type],
        prefix=Path(filename).stem
    )

    # 10. Final response
    return {
        "document_id": document_id,
        "filename": filename,
        "file_type": ext,
        "page_count": page_count,
        "sheet_count": sheet_count,
        "language": language,
        "num_blocks": len(cleaned_blocks),
        "num_chunks": len(chunks_with_type),
        "sample_chunk": chunks_with_type[0]["text"][:300] if chunks_with_type else "",
        "saved_chunks": saved_paths[:5],
        "status": "EMBEDDED"
    }
