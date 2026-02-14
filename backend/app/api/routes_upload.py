from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.core.config import settings
from app.services.document_service import process_upload
from app.api.deps import get_current_user

router = APIRouter(prefix="/files", tags=["upload"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
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

    # ✅ SAME user_id AS CHAT (JWT sub)
    user_id = current_user["sub"]

    return process_upload(
        file_bytes=file_bytes,
        filename=file.filename,
        user_id=user_id
    )
