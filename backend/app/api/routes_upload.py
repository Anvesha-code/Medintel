# app/api/routes_upload.py
from fastapi import APIRouter, UploadFile, HTTPException
from pathlib import Path
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.chunker import chunk_text
from app.services.rag_pipeline import RAGPipeline
import shutil

router = APIRouter(prefix="/upload", tags=["upload"])
rag = RAGPipeline()

UPLOAD_DIR = Path("data/uploads_tmp")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/")

async def upload(file: UploadFile):
    file_path = UPLOAD_DIR / file.filename
    print("calls post /")
    try:

        # Save file
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Extract and chunk
        text = extract_text_from_pdf(file_path)
        chunks = chunk_text(text)
        print("chunks created")
        if not chunks:
            raise HTTPException(status_code=400, detail="No text extracted from PDF")

            print("insert ")
        rag.insert_docs(chunks)

        return {"message": "PDF processed and stored!", "chunks": len(chunks)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        #It does nothing.

        #But it is kept for optional cleanup code, like:

        #Deleting temporary uploaded file
        # optional: remove uploaded file (uncomment if desired)
        # try: file_path.unlink(missing_ok=True)
        # except Exception: pass

        # Closing a connection
        pass
