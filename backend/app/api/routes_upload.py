# app/api/routes_upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException

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

    # Now this matches our extractor signature
    result = extract_text_from_pdf(pdf_bytes)

    return {
        "filename": file.filename,
        "num_pages": len(result["pages"]),
        "sample_page_1": result["pages"][0]["text"][:500] if result["pages"] else "",
        "full_text_length": len(result["full_text"])
    }
