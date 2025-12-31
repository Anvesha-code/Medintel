# app/services/prompt_builder.py
from typing import List, Dict

class PromptBuilder:

    @staticmethod
    def build(question: str, contexts: List[Dict]) -> str:
        """
        Build a controlled RAG prompt using retrieved chunks
        """

        context_blocks = []

        for ctx in contexts:
            context_blocks.append(
                f"""
[CHUNK_ID: {ctx['chunk_id']}]
[SOURCE_TYPE: {ctx['source_type']}]
CONTENT:
{ctx['text']}
"""
            )

        full_context = "\n".join(context_blocks)

        prompt = f"""
You are a domain-aware assistant.

STRICT RULES:
1. Answer ONLY using the provided context.
2. If the answer is not present, say: "Information not found in documents".
3. Always mention CHUNK_ID in your answer.
4. Formatting rules:
   - If SOURCE_TYPE is csv or table → respond in markdown table.
   - Otherwise → respond in bullet points or short paragraphs.

QUESTION:
{question}

CONTEXT:
{full_context}

FINAL ANSWER (with citations):
"""

        return prompt.strip()
