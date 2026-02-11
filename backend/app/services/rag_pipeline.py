from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.prompt_builder import PromptBuilder
from app.services.llm_client import OllamaLLM
import re
#from app.services.llm_client import OpenAILLM


class RAGPipeline:
    def __init__(self):
        self._embedder = EmbeddingService()
        self._vdb = VectorStore()
        self._llm = OllamaLLM(model="tinyllama:latest")
        #self._llm = OpenAILLM(model="gpt-4o-mini")



    def search(self, question, user_id, document_id=None):

        print("\n🚀 RAGPipeline.search() CALLED")
        print("🔎 User Query:", question)
        print("👤 User ID:", user_id)
        print("📄 Document ID:", document_id)

        # 1️⃣ Generate query embedding
        query_embedding = self._embedder.generate_embedding(question)
        print("✅ Query embedding generated")

        retrieved_hits = []

        # 2️⃣ Search TEXT chunks
        text_hits = self._vdb.search(
            query_embedding=query_embedding,
            user_id=user_id,
            document_id=document_id,
            source_type="text",
            top_k=4
        )

        print("\n📄 TEXT SEARCH RESULTS:")
        for i, hit in enumerate(text_hits, 1):
            payload = hit.payload or {}
            print(f"\n--- Text Hit {i} ---")
            print("Score:", hit.score)
            print("Doc ID:", payload.get("doc_id"))
            print("Chunk Index:", payload.get("chunk_index"))
            print("Text:", payload.get("text", "")[:400])

        retrieved_hits.extend(text_hits)

        # 3️⃣ Search TABLE chunks
        table_hits = self._vdb.search(
            query_embedding=query_embedding,
            user_id=user_id,
            document_id=document_id,
            source_type="table",
            top_k=4
        )

        print("\n📊 TABLE SEARCH RESULTS:")
        for i, hit in enumerate(table_hits, 1):
            payload = hit.payload or {}
            print(f"\n--- Table Hit {i} ---")
            print("Score:", hit.score)
            print("Doc ID:", payload.get("doc_id"))
            print("Chunk Index:", payload.get("chunk_index"))
            print("Text:", payload.get("text", "")[:400])

        retrieved_hits.extend(table_hits)

        # 4️⃣ Fallback search
        if not retrieved_hits:
            print("\n⚠️ No hits found, running fallback search...")
            retrieved_hits = self._vdb.search(
                query_embedding=query_embedding,
                user_id=user_id,
                source_type=None,
                document_id=document_id,
                top_k=3
            )
        print("hello this is", retrieved_hits)
        # 5️⃣ Prepare context
        contexts = self._prepare_context(retrieved_hits)[:4]

        print("\n🧠 CONTEXT SENT TO LLM:")
        for i, ctx in enumerate(contexts, 1):
            print(f"\n--- Context {i} ---")
            print("Doc ID:", ctx["doc_id"])
            print("Source Type:", ctx["source_type"])
            print("Score:", ctx["score"])
            print("Text:", ctx["text"][:500])

        # 6️⃣ Build prompt
        # 6️⃣ Build prompts (SYSTEM + USER)

        system_prompt = """
        You are MedIntel, a medical prescription question-answering assistant.

        STRICT RULES:
        - Answer ONLY using the provided CONTEXT
        - Use exact wording from the document
        - If the answer is present, say YES and quote it
        - If truly absent, say: "Not mentioned in the prescription"
        - Do NOT invent or infer
        - Do NOT explain reasoning
        - Do NOT repeat the rules

        Diagnosis Questions:
        - Extract text under “Diagnosis” or “Diagnosis / Complaint”

        Medicine Questions:
        - Extract ALL medicine names exactly as written
        - Include dosage/frequency (OD, BD, TDS, mg, ORS, etc.)
        - Return medicines as bullet list

        Yes/No Questions:
        - Answer "Yes" or "No" only if explicitly supported
        - After Yes/No, quote the exact supporting line
        """

        user_prompt = PromptBuilder.build(
            question=question,
            contexts=contexts
        )

        combined_prompt = f"""
        You are MedIntel.

        Follow these rules strictly:
        - Answer ONLY using the CONTEXT below
        - Use exact wording from the document
        - If present, say YES and quote it
        - If absent, say: Not mentioned in the prescription
        - Do NOT explain
        - Do NOT repeat instructions

        ---------------------
        CONTEXT:
        ---------------------
        {user_prompt}

        ---------------------
        FINAL ANSWER:
        ---------------------
        """

        print("\n📝 FINAL PROMPT (first 300 chars):")
        print(combined_prompt[:300])

        answer = self._llm.generate(prompt=combined_prompt)

        print("\n🤖 RAW LLM ANSWER:")
        print(answer)

        answer = self._block_hallucinations(answer, contexts)

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
    # Context preparation logic
    # =========================
    def _prepare_context(self, hits):
        contexts = []

        for hit in hits:
            payload = hit.payload or {}
            text = (payload.get("text") or "").strip()

            if len(text) < 10:
                continue

            lowered = text.lower()
            if any(x in lowered for x in ["signature", "stamp", "sen.", "____"]):
                continue

            section_type = payload.get("section_type", "general")
            score = hit.score

            if section_type in {"diagnosis", "treatment", "medication"}:
                score += 0.15

            contexts.append({
                "chunk_id": payload.get("chunk_id", hit.id),
                "doc_id": payload.get("doc_id"),
                "source_type": payload.get("source_type", "text"),
                "chunk_index": payload.get("chunk_index"),
                "text": text,
                "score": score
            })

        contexts = self._merge_adjacent_chunks(contexts)
        contexts.sort(key=lambda x: x["score"], reverse=True)
        return contexts

    # =========================
    # Overlap merge logic
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

    # =========================
    # Hallucination protection
    # =========================
    def _block_hallucinations(self, answer: str, contexts) -> str:
        if not answer or not answer.strip():
            return "Not mentioned in the prescription."

        answer_lower = answer.lower()
        context_text = " ".join(c["text"].lower() for c in contexts)

        medical_terms = [
            # 🔹 Common diagnoses / conditions
            "acute", "chronic", "infection", "inflammation",
            "gastroenteritis", "diabetes", "hypertension",
            "asthma", "anemia", "fever", "pain",
            "vomiting", "diarrhea", "nausea", "cough",
            "headache", "dizziness", "fatigue",

            # 🔹 Medicines & dosage forms
            "tablet", "tab", "capsule", "cap", "syrup", "suspension",
            "injection", "inj", "ointment", "cream", "drops",
            "solution", "powder",

            # 🔹 Dosage & frequency terms
            "mg", "ml", "mcg", "g",
            "od", "bd", "tds", "qid",
            "hs", "stat", "sos",
            "once daily", "twice daily", "thrice daily",

            # 🔹 Treatment & care
            "treatment", "therapy", "medication", "prescribed",
            "advised", "recommended", "continue", "stop",
            "follow up", "review",

            # 🔹 Lab tests & vitals
            "blood pressure", "bp", "pulse", "temperature",
            "cbc", "hemoglobin", "hb",
            "sugar", "glucose", "cholesterol",
            "urine", "urinalysis", "ecg", "x-ray", "ultrasound",

            # 🔹 Medical departments & context
            "diagnosis", "complaint", "history", "examination",
            "assessment", "impression", "plan",

            # 🔹 Advice & lifestyle
            "rest", "hydration", "fluids",
            "diet", "exercise", "avoid", "limit",
            "ors", "iv fluids"]

        if any(term in answer_lower for term in medical_terms):
            return answer.strip()

        if any(word in context_text for word in answer_lower.split() if len(word) > 4):
            return answer.strip()

        return "Not mentioned in the prescription."
