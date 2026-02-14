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
        print("✅ Query embedding generated")

        # 2️⃣ Retrieve relevant chunks
        retrieved_hits = []

        print("\n🔍 Searching TEXT chunks")
        text_hits = self._vdb.search(
            query_embedding=query_embedding,
            user_id=user_id,
            document_id=document_id,
            source_type="text",
            top_k=4
        )
        retrieved_hits.extend(text_hits)

        print("\n🔍 Searching TABLE chunks")
        table_hits = self._vdb.search(
            query_embedding=query_embedding,
            user_id=user_id,
            document_id=document_id,
            source_type="table",
            top_k=4
        )
        retrieved_hits.extend(table_hits)

        print(f"\n📦 Total retrieved hits (before fallback): {len(retrieved_hits)}")

        # 3️⃣ Fallback search if nothing found
        if not retrieved_hits:
            print("⚠️ No hits found, running fallback search")
            retrieved_hits = self._vdb.search(
                query_embedding=query_embedding,
                user_id=user_id,
                document_id=document_id,
                source_type=None,
                top_k=3
            )

        print(f"📦 Total retrieved hits (after fallback): {len(retrieved_hits)}")

        # 🔴 DEBUG RAW HITS
        for i, h in enumerate(retrieved_hits, 1):
            print(f"\n--- RAW HIT {i} ---")
            print("Score:", h.score)
            print("Doc ID:", h.payload.get("doc_id"))
            print("Chunk Index:", h.payload.get("chunk_index"))
            print("Text Preview:", h.payload.get("text", "")[:200])

        # 4️⃣ Prepare clean context
        contexts = self._prepare_context(retrieved_hits)

        print(f"\n🧹 Contexts after cleaning: {len(contexts)}")

        for i, ctx in enumerate(contexts, 1):
            print(f"\n--- CLEAN CONTEXT {i} ---")
            print("Score:", ctx["score"])
            print(ctx["text"][:400])

        # 5️⃣ Build context text
        context_text = PromptBuilder.build_context_only(contexts)
        print("\n🧠 FINAL CONTEXT TEXT LENGTH:", len(context_text))
        print(context_text[:600])

        # 6️⃣ Prompt
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

        print("\n🧾 PROMPT SENT TO LLM:")
        print(combined_prompt[:800])

        # 7️⃣ Generate answer
        answer = self._llm.generate(prompt=combined_prompt)

        print("\n🤖 RAW LLM OUTPUT:")
        print(answer)

        answer = (answer or "").strip()

        if not answer:
            print("❌ LLM RETURNED EMPTY ANSWER")

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
    # Context cleaning
    # =========================
    def _prepare_context(self, hits):
        contexts = []

        for hit in hits:
            payload = hit.payload or {}
            text = (payload.get("text") or "").strip()

            print("\n🧪 CLEANING CHECK")
            print("Original length:", len(text))
            print("Preview:", text[:150])

            # Drop very small fragments
            if len(text) < 20:
                print("❌ Dropped: too short")
                continue

            alpha_ratio = sum(c.isalpha() for c in text) / max(len(text), 1)
            print("Alpha ratio:", alpha_ratio)

            if alpha_ratio < 0.3:
                print("❌ Dropped: low alpha ratio")
                continue

            lowered = text.lower()
            boilerplate = ["page ", "copyright", "all rights reserved"]
            if any(b in lowered for b in boilerplate) and alpha_ratio < 0.5:
                print("❌ Dropped: boilerplate")
                continue

            print("✅ Accepted")

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
