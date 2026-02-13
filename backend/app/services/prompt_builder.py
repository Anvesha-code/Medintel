class PromptBuilder:

    @staticmethod
    def build_context_only(contexts):
        if not contexts:
            return "No relevant information found in the document."

        return "\n\n".join(
            ctx["text"]
            for ctx in contexts
            if ctx.get("text")
        )
