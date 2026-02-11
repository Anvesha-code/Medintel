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
CONTEXT:
{context_text}

QUESTION:
{question}
"""
