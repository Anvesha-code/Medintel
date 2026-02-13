from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.prompt_builder import PromptBuilder
from app.services.llm_client import OpenAILLM


class RAGPipeline:
    def __init__(self):
        self._embedder = EmbeddingService()
        self._vdb = VectorStore()
        self._llm = OpenAILLM(model="gpt-4o-mini")

    def search(self, question, user_id, document_id=None):

        print("\n🚀 RAGPipeline.search() CALLED")
        print("🔎 Question:", question)
        print("👤 User ID:", user_id)
        print("📄 Document ID:", document_id)

        # 1️⃣ Generate embedding for the question
        query_embedding = self._embedder.generate_embedding(question)

        # 2️⃣ Retrieve relevant chunks
        retrieved_hits = []

        retrieved_hits.extend(
            self._vdb.search(
                query_embedding=query_embedding,
                user_id=user_id,
                document_id=document_id,
                source_type="text",
                top_k=4
            )
        )

        retrieved_hits.extend(
            self._vdb.search(
                query_embedding=query_embedding,
                user_id=user_id,
                document_id=document_id,
                source_type="table",
                top_k=4
            )
        )

        # 3️⃣ Fallback search if nothing found
        if not retrieved_hits:
            retrieved_hits = self._vdb.search(
                query_embedding=query_embedding,
                user_id=user_id,
                document_id=document_id,
                source_type=None,
                top_k=3
            )

        # 4️⃣ Prepare clean, generic context
        contexts = self._prepare_context(retrieved_hits)[:4]

        print("\n🧠 CONTEXT SENT TO LLM:")
        for i, ctx in enumerate(contexts, 1):
            print(f"\n--- Context {i} ---")
            print(ctx["text"][:400])

        # 5️⃣ Build document-only context text
        context_text = PromptBuilder.build_context_only(contexts)

        # 6️⃣ Universal prompt (NO domain logic)
        combined_prompt = f"""
CONTEXT:
{context_text}

QUESTION:
{question}

INSTRUCTION:
Answer the question using ONLY the CONTEXT above.
Use exact wording from the document.
If the answer is not present, reply exactly:
Not mentioned in the document.

ANSWER:
"""

        # 7️⃣ Generate answer
        answer = self._llm.generate(prompt=combined_prompt)
        answer = answer.strip()

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

    # =========================
    # Generic context cleaning
    # =========================
    def _prepare_context(self, hits):
        contexts = []

        for hit in hits:
            payload = hit.payload or {}
            text = (payload.get("text") or "").strip()

            # Drop very small fragments
            if len(text) < 20:
                continue

            # Drop symbol-heavy noise
            alpha_ratio = sum(c.isalpha() for c in text) / max(len(text), 1)
            if alpha_ratio < 0.3:
                continue

            # Drop generic boilerplate (document-agnostic)
            lowered = text.lower()
            boilerplate = ["page ", "copyright", "all rights reserved"]
            if any(b in lowered for b in boilerplate) and alpha_ratio < 0.5:
                continue

            contexts.append({
                "chunk_id": payload.get("chunk_id", hit.id),
                "doc_id": payload.get("doc_id"),
                "source_type": payload.get("source_type", "text"),
                "chunk_index": payload.get("chunk_index"),
                "text": text,
                "score": hit.score
            })

        contexts = self._merge_adjacent_chunks(contexts)
        contexts.sort(key=lambda x: x["score"], reverse=True)
        return contexts

    # =========================
    # Merge adjacent chunks
    # =========================
    def _merge_adjacent_chunks(self, contexts):
        merged = []
        contexts.sort(key=lambda x: (x["doc_id"], x.get("chunk_index", -1)))

        for ctx in contexts:
            if (
                merged
                and ctx["doc_id"] == merged[-1]["doc_id"]
                and ctx.get("chunk_index") is not None
                and merged[-1].get("chunk_index") is not None
                and ctx["chunk_index"] == merged[-1]["chunk_index"] + 1
            ):
                merged[-1]["text"] += " " + ctx["text"]
                merged[-1]["score"] = max(merged[-1]["score"], ctx["score"])
            else:
                merged.append(ctx)

        return merged
