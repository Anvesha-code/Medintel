from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.utils.file_type import detect_file_type

from app.services.text_processing import (
    clean_text_pages,
    chunk_text,
    chunk_table_text,
    chunk_audio_transcript,
    save_chunks_locally,
)
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.image_extractor import extract_text_from_image
from app.services.docx_extractor import extract_text_from_docx
from app.services.pptx_extractor import extract_text_from_pptx
from app.services.spreadsheet_extractor import extract_text_from_spreadsheet
from app.services.html_extractor import extract_text_from_html
from app.services.audio_transcriber import transcribe_audio
from app.services.txt_extractor import extract_text_from_txt


def process_upload(file_bytes: bytes, filename: str) -> dict:
    mime, ext = detect_file_type(filename, file_bytes)
    mime = mime or ""
    ext = (ext or "").lower()

    source_type: Optional[str] = None
    extract_result: Optional[dict] = None

    # ---------- EXTRACTION ----------
    if "pdf" in mime or ext == "pdf":
        extract_result = extract_text_from_pdf(file_bytes)
        source_type = "pdf"

    elif mime.startswith("image/") or ext in ("jpg", "jpeg", "png", "tiff", "bmp"):
        extract_result = extract_text_from_image(file_bytes)
        source_type = "image"

    elif ext in ("docx", "doc"):
        extract_result = extract_text_from_docx(file_bytes)
        source_type = "docx"

    elif ext in ("ppt", "pptx"):
        extract_result = extract_text_from_pptx(file_bytes)
        source_type = "pptx"

    elif ext in ("xls", "xlsx", "csv"):
        extract_result = extract_text_from_spreadsheet(file_bytes, filename=filename)
        source_type = "spreadsheet"

    elif ext in ("html", "htm") or "text/html" in mime:
        extract_result = extract_text_from_html(file_bytes)
        source_type = "html"

    elif mime.startswith("audio/") or ext in ("mp3", "wav", "m4a", "ogg"):
        if not settings.ENABLE_AUDIO:
            raise ValueError("Audio transcription disabled")
        extract_result = transcribe_audio(file_bytes, filename=filename)
        source_type = "audio"

    elif mime.startswith("text/") or ext in ("txt", "md", "log"):
        extract_result = extract_text_from_txt(file_bytes)
        source_type = "text"

    else:
        raise ValueError(f"Unsupported file type: {mime}/{ext}")

    if not extract_result or "pages" not in extract_result:
        raise RuntimeError("Extractor returned no pages")

    # ---------- CLEANING ----------
    pages = extract_result["pages"]
    meta = extract_result.get("meta", {})

    full_text, cleaned_pages = clean_text_pages(pages, source_type)

    # ---------- CHUNKING ----------
    if source_type == "spreadsheet":
        chunks = []
        for cp in cleaned_pages:
            chunks.extend(chunk_table_text(cp, chunk_size=settings.CHUNK_SIZE))

    elif source_type == "audio":
        transcript = "\n\n".join(p for p in cleaned_pages if p)
        chunks = chunk_audio_transcript(
            transcript,
            chunk_chars=settings.AUDIO_CHUNK_CHARS,
            overlap=settings.AUDIO_CHUNK_OVERLAP
        )

    else:
        chunks = chunk_text(
            full_text,
            chunk_size=settings.CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP
        )

    # ---------- SAVE ----------
    saved_files = []
    if settings.SAVE_CHUNKS:
        prefix = Path(filename).stem
        saved_files = save_chunks_locally(chunks, prefix=prefix)

    return {
        "filename": filename,
        "source_type": source_type,
        "mime": mime,
        "meta": meta,
        "num_pages": len(pages),
        "num_cleaned_pages": len([p for p in cleaned_pages if p]),
        "num_chunks": len(chunks),
        "sample_chunk": chunks[0][:500] if chunks else "",
        "saved_chunk_files": saved_files[:10],
        "full_text_length": len(full_text),
    }
