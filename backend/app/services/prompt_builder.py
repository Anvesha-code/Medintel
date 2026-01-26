class PromptBuilder:
    @staticmethod
    def build(question: str, contexts: list) -> str:
        if not contexts:
            context_text = "No relevant information found in the document."
        else:
            context_text = "\n\n".join(
                f"[Doc {c['doc_id']} | Chunk {c['chunk_index']}]\n{c['text']}"
                for c in contexts
            )

        return f"""
You are MedIntel, a medical document question-answering assistant.

RULES (STRICT):
- Answer ONLY using the CONTEXT below
- Use exact wording from the document
- If the answer is present, say YES and quote it
- If truly absent, say: "Not mentioned in the prescription"
- Do NOT invent or infer

QUESTION:
{question}

CONTEXT:
{context_text}

ANSWER:
"""
