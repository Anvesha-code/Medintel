from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStore


class RAGPipeline:
    def __init__(self):
        self._embedder = EmbeddingService()
        self._vdb = VectorStore()

    def search(self, query: str, limit: int = 5):
        print("🚀 RAGPipeline.search() CALLED")
        query_embedding = self._embedder.generate_embedding([query])[0]
        print("🧠 Embedding generated, length:", len(query_embedding))
        return self._vdb.search(
            query_embedding=query_embedding,
            top_k=limit
        )
