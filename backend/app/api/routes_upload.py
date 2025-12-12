# app/api/routes_upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.text_processing import clean_text_pages, chunk_text, save_chunks_locally
from pathlib import Path

from app.services.pdf_extractor import extract_text_from_pdf

router = APIRouter(prefix="/files", tags=["upload"])  # prefix explains /files/upload


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for now")

    # Read raw bytes
    pdf_bytes = await file.read()
    result = extract_text_from_pdf(pdf_bytes)

    # --- clean pages and produce a combined full_text ---
    full_text, cleaned_pages = clean_text_pages(result["pages"])

    # --- chunk the cleaned full text ---
    # tune chunk_size and overlap as needed
    chunks = chunk_text(full_text, chunk_size=500, overlap=50)

    # --- save chunks locally for inspection ---
    # use the file stem (filename without extension) as prefix
    prefix = Path(file.filename).stem
    saved_files = save_chunks_locally(chunks, prefix=prefix)
    return {
        "filename": file.filename,
        "num_pages": len(result["pages"]),
        "num_cleaned_pages": len([p for p in cleaned_pages if p]),
        "num_chunks": len(chunks),
        "sample_chunk": chunks[0][:500] if chunks else "",
        "saved_chunk_files": saved_files[:10],  # show first 10 paths
        "full_text_length": len(full_text)
    }