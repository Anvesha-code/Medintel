# app/api/routes_chat.py
import asyncio
from fastapi import APIRouter, Query, HTTPException, Depends
from app.services.rag_pipeline import RAGPipeline
from app.api.deps import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])
rag = RAGPipeline()



@router.post("/ask")
async def ask(
    question: str = Query(..., min_length=1),
    #user_id: int = Query(...),
    current_user: dict = Depends(get_current_user),
    document_id: int = Query(..., description="Must be a valid document_id")

):
    """
        Authenticated chat endpoint.
        User identity is extracted from JWT.
        """

    # ✅ user_id comes ONLY from JWT
    user_id = current_user["sub"]

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

        return {
            "answer_chunks": [
                {
                    "answer": results["answer"],
                    "sources": results["sources"]
                }
            ]
        }


    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="RAG search took too long, request timed out."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


