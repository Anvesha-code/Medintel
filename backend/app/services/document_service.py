from pathlib import Path
from app.utils.file_type import detect_file_type
from app.services.extraction_dispatcher import extract_text
from app.services.text_processing import (
    clean_text_blocks,
    chunk_text,
    chunk_table_text,
    save_chunks_locally
)
from app.db.db import get_connection


def process_upload(file_bytes: bytes, filename: str) -> dict:
    # ---- Detect file type ----
    mime, ext = detect_file_type(filename, file_bytes)

    # ---- Extract raw content ----
    extraction = extract_text(file_bytes, filename, mime)
    text_blocks = extraction["text_blocks"]
    meta = extraction.get("meta", {})

    page_count = meta.get("page_count")
    sheet_count = meta.get("sheet_count")
    language = meta.get("language")

    # ---- Clean text ----
    cleaned_blocks = clean_text_blocks(text_blocks)

    # ---- Chunking ----
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

    # ---- Save document metadata (DB) ----
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO documents
        (filename, file_type, page_count, sheet_count, language, extraction_status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (filename, ext, page_count, sheet_count, language, "CHUNKED")
    )
    document_id = cur.lastrowid

    # ---- Save chunks (DB) ----
    for idx, chunk in enumerate(chunks):
        cur.execute(
            """
            INSERT INTO chunks (document_id, chunk_index, chunk_text, source_type)
            VALUES (?, ?, ?, ?)
            """,
            (document_id, idx, chunk, cleaned_blocks[0]["source_type"])
        )

    conn.commit()
    conn.close()

    # ---- Save chunks locally (debug / temp) ----
    saved_paths = save_chunks_locally(chunks, prefix=Path(filename).stem)

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
        "status": "CHUNKED"
    }
