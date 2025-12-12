# app/api/routes_upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from typing import Optional

from app.services.text_processing import (
    clean_text_pages,
    chunk_text,
    chunk_table_text,
    chunk_audio_transcript,
    save_chunks_locally,
)
from app.utils.file_type import detect_file_type
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.image_extractor import extract_text_from_image
from app.services.docx_extractor import extract_text_from_docx
from app.services.pptx_extractor import extract_text_from_pptx
from app.services.spreadsheet_extractor import extract_text_from_spreadsheet
from app.services.html_extractor import extract_text_from_html
from app.services.audio_transcriber import transcribe_audio
from app.services.txt_extractor import extract_text_from_txt

router = APIRouter(prefix="/files", tags=["upload"])

# Maximum in-memory read (20 MB). Larger files should be handled with temp files.
MAX_MEM_READ = 20 * 1024 * 1024


async def _read_uploadfile(upload: UploadFile) -> bytes:
    """
    Read upload content into memory. For large files (> MAX_MEM_READ)
    you should stream to a temp file and pass path to extractor instead.
    """
    contents = await upload.read()
    return contents


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # read bytes (for larger files you may stream to disk and pass path to extractors)
    file_bytes = await _read_uploadfile(file)
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    mime, ext = detect_file_type(file.filename, file_bytes)
    mime = mime or ""  # guard if detect_file_type returns None
    ext = (ext or "").lower()

    source_type: Optional[str] = None
    extract_result: Optional[dict] = None

    # Dispatch based on mime or extension
    try:
        # PDF
        if "pdf" in mime or ext == "pdf":
            extract_result = extract_text_from_pdf(file_bytes)
            source_type = "pdf"

        # Images
        elif mime.startswith("image/") or ext in ("jpg", "jpeg", "png", "tiff", "bmp"):
            extract_result = extract_text_from_image(file_bytes)
            source_type = "image"

        # Word
        elif ext in ("docx", "doc"):
            extract_result = extract_text_from_docx(file_bytes)
            source_type = "docx"

        # PowerPoint
        elif ext in ("ppt", "pptx"):
            extract_result = extract_text_from_pptx(file_bytes)
            source_type = "pptx"

        # Excel/CSV
        elif ext in ("xls", "xlsx", "csv"):
            extract_result = extract_text_from_spreadsheet(file_bytes, filename=file.filename)
            source_type = "spreadsheet"

        # HTML
        elif ext in ("html", "htm") or "text/html" in mime:
            extract_result = extract_text_from_html(file_bytes)
            source_type = "html"

        # Audio
        elif mime.startswith("audio/") or ext in ("mp3", "wav", "m4a", "ogg"):
            extract_result = transcribe_audio(file_bytes, filename=file.filename)
            source_type = "audio"

        # Plain text
        elif mime.startswith("text/") or ext in ("txt", "md", "log"):
            extract_result = extract_text_from_txt(file_bytes)
            source_type = "text"

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {mime}/{ext}")

    except HTTPException:
        raise
    except Exception as e:
        # Keep the error detail short for API response, but raise 500
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

    if not extract_result or "pages" not in extract_result:
        raise HTTPException(status_code=500, detail="Extractor returned no pages")

    pages = extract_result.get("pages", [])
    meta = extract_result.get("meta", {})

    # --- CLEANING: pass source_type so cleaner can adapt ---
    full_text, cleaned_pages = clean_text_pages(pages, source_type)

    # --- CHUNKING: select chunking strategy based on source_type ---
    chunks = []
    if source_type == "spreadsheet":
        # Use table row based chunking for each cleaned page
        for cp in cleaned_pages:
            # cp contains textualized rows; chunk_table_text will split by rows
            chunks.extend(chunk_table_text(cp, chunk_size=400))
    elif source_type == "audio":
        # Audio transcripts may be long; split by chars/time windows
        transcript = "\n\n".join([p for p in cleaned_pages if p])
        chunks = chunk_audio_transcript(transcript, chunk_chars=1500, overlap=100)
    else:
        # default: character-based chunking for prose content
        chunks = chunk_text(full_text, chunk_size=500, overlap=50)

    # --- save chunks locally for inspection (MVP) ---
    prefix = Path(file.filename).stem
    saved_files = save_chunks_locally(chunks, prefix=prefix)

    return {
        "filename": file.filename,
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
