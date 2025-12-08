# app/services/rag_pipeline.py
from app.services.embeddings import Embeddings
from app.services.vector_store import VectorStore
from typing import List

class RAGPipeline:
    def __init__(self):
        self.embedder = Embeddings()
        self.vdb = VectorStore()

    def insert_docs(self, chunks: List[str]):
        if not chunks:
            return "No chunks received"

        vectors = self.embedder.embed(chunks)
        payloads = [{"text": c} for c in chunks]
        self.vdb.insert_vectors(vectors, payloads)
        return "Inserted Successfully"

    def search(self, query: str, top_k: int = 5) -> List[str]:
        if not query or not query.strip():
            return []

        q_vec = self.embedder.embed([query])[0]
        results = self.vdb.search(q_vec, top_k)

        # results may be different shapes depending on qdrant client:
        texts = []
        for r in results:
            # r might be ScoredPoint with .payload or dict with 'payload'
            payload = None
            if hasattr(r, "payload"):
                payload = r.payload
            elif isinstance(r, dict):
                payload = r.get("payload", {})
            elif hasattr(r, "point") and hasattr(r.point, "payload"):
                payload = r.point.payload
            if payload:
                texts.append(payload.get("text", "") if isinstance(payload, dict) else "")
        return texts
