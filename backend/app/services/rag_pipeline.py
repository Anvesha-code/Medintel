from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.prompt_builder import PromptBuilder
from app.services.llm_client import OllamaLLM


class RAGPipeline:
    def __init__(self):
        self._embedder = EmbeddingService()
        self._vdb = VectorStore()
        self._llm = OllamaLLM(model="tinyllama:latest")

    def search(self, query: str, user_id: str):
        print("🚀 RAGPipeline.search() CALLED")

        # 1️⃣ Generate embedding
        query_embedding = self._embedder.generate_embedding(query)

        retrieved_hits = []

        # 2️⃣ Search TEXT
        retrieved_hits.extend(
            self._vdb.search(
                query_embedding=query_embedding,
                user_id=user_id,
                source_type="text",
                top_k=6
            )
        )

        # 3️⃣ Search TABLE
        retrieved_hits.extend(
            self._vdb.search(
                query_embedding=query_embedding,
                user_id=user_id,
                source_type="table",
                top_k=2
            )
        )

        # 4️⃣ Fallback search
        if not retrieved_hits:
            retrieved_hits = self._vdb.search(
                query_embedding=query_embedding,
                user_id=user_id,
                source_type=None,
                top_k=5
            )

        # 5️⃣ Prepare context
        contexts = self._prepare_context(retrieved_hits)[:4]

        # 6️⃣ Build prompt (UNCHANGED)
        prompt = PromptBuilder.build(
            question=query,
            contexts=contexts
        )

        print("PROMPT SENT TO LLM (first 300 chars):")
        print(prompt[:300])

        # 7️⃣ Call LLM
        answer = self._llm.generate(prompt)
        print("RAW LLM ANSWER:", answer)

        # ✅ HARD hallucination guard
        answer = self._block_hallucinations(answer, contexts)

        # 8️⃣ Deduplicate sources
        unique_sources = {
            c["chunk_id"]: {
                "chunk_id": c["chunk_id"],
                "source_type": c["source_type"],
                "doc_id": c["doc_id"]
            }
            for c in contexts
        }

        return {
            "answer": answer,
            "sources": list(unique_sources.values())
        }

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

    def _block_hallucinations(self, answer: str, contexts) -> str:
        if not answer or not answer.strip():
            return "Not mentioned in the prescription."

        answer_lower = answer.lower()

        hallucination_markers = [
            "xyz",
            "generic medication",
            "general medical condition",
            "intended use",
            "overview",
            "expiration date",
            "affiliate",
            "prevents symptoms",
            "example",
            "such as"
        ]

        for marker in hallucination_markers:
            if marker in answer_lower:
                return "Not mentioned in the prescription."

        context_text = " ".join(
            c["text"].lower() for c in contexts if c.get("text")
        )

        shared_tokens = [
            token for token in answer_lower.split()
            if token in context_text and len(token) > 4
        ]

        if not shared_tokens:
            return "Not mentioned in the prescription."

        return answer.strip()
