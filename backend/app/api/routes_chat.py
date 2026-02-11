# app/api/routes_chat.py
import asyncio
from fastapi import APIRouter, Query, HTTPException
from app.services.rag_pipeline import RAGPipeline


router = APIRouter(prefix="/chat", tags=["chat"])
rag = RAGPipeline()

@router.post("/ask")
async def ask(
    question: str = Query(..., min_length=1),
    user_id: int = Query(...),
    document_id: int | None = Query(None)
):
    try:
        results = await asyncio.wait_for(
            asyncio.to_thread(
                rag.search,
                question,
                user_id,
                document_id
            ),
            timeout=300
        )

        return {"answer_chunks": results}

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="RAG search took too long, request timed out."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


