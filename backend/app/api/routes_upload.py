from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.core.config import settings
from app.services.document_service import process_upload

router = APIRouter(prefix="/files", tags=["upload"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: int = 5   # later replace with auth dependency
):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(file_bytes) > settings.MAX_MEM_READ:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.MAX_UPLOAD_MB} MB limit"
        )

    return process_upload(
        file_bytes=file_bytes,
        filename=file.filename,
        user_id=user_id
    )
