from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.prompt_builder import PromptBuilder
from app.services.llm_client import OllamaLLM


class RAGPipeline:
    def __init__(self):
        self._embedder = EmbeddingService()
        self._vdb = VectorStore()
        self._llm = OllamaLLM(model="mistral")

    def search(self, query: str, user_id: str):
        print("🚀 RAGPipeline.search() CALLED")

        # 1️⃣ Generate query embedding
        query_embedding = self._embedder.generate_embedding(query)
        print("🧠 Embedding generated, length:", len(query_embedding))

        retrieved_hits = []

        # 2️⃣ Search TEXT chunks
        text_results = self._vdb.search(
            query_embedding=query_embedding,
            user_id=user_id,
            source_type="text",
            top_k=6
        )
        retrieved_hits.extend(text_results)

        # 3️⃣ Search TABLE chunks
        table_results = self._vdb.search(
            query_embedding=query_embedding,
            user_id=user_id,
            source_type="table",
            top_k=2
        )
        retrieved_hits.extend(table_results)

        # 4️⃣ Fallback search
        if not retrieved_hits:
            print("⚠️ No filtered results. Falling back to user-only search.")
            retrieved_hits = self._vdb.search(
                query_embedding=query_embedding,
                user_id=user_id,
                source_type=None,
                top_k=5
            )

        # 5️⃣ Prepare context for prompt
        contexts = self._prepare_context(retrieved_hits)

        # 6️⃣ Build prompt (DAY-10 CORE)
        prompt = PromptBuilder.build(
            question=query,
            contexts=contexts
        )

        # 7️⃣ Call LLM
        answer = self._llm.generate(prompt)

        return {
            "answer": answer,
            "sources": [
                {
                    "chunk_id": c["chunk_id"],
                    "source_type": c["source_type"],
                    "doc_id": c["doc_id"]
                }
                for c in contexts
            ]
        }

    # 🔽 NEW: Context preparation for prompt builder
    def _prepare_context(self, hits):
        contexts = []

        for hit in hits:
            payload = hit.payload

            contexts.append({
                "chunk_id": payload.get("chunk_id", hit.id),
                "doc_id": payload.get("doc_id"),
                "source_type": payload.get("source_type", "text"),
                "text": payload.get("text", "")
            })

        return contexts
