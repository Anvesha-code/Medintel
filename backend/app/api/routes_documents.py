# app/api/routes_documents.py
from fastapi import APIRouter

router = APIRouter(tags=["documents"])

# Temporary fake storage – replace with DB / Qdrant metadata later
fake_documents = [
    {"id": 1, "name": "example1.pdf"},
    {"id": 2, "name": "example2.docx"},
]

@router.get("/documents")
async def list_documents():
    return {"documents": fake_documents}
