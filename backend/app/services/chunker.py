# app/services/chunker.py
def chunk_text(text: str, chunk_size: int = 350, overlap: int = 40):
    """
    Splits text into word-based chunks.
    Optimized for academic and RAG-based retrieval.
    """
    if not text:
        return []

    # Remove excessive whitespace
    text = " ".join(text.split())

    words = text.split()
    if chunk_size <= overlap:
        overlap = 0

    chunks = []
    i = 0
    n = len(words)

    while i < n:
        chunk_words = words[i:i + chunk_size]
        chunk = " ".join(chunk_words)

        # ❗ Skip very small or noisy chunks
        if len(chunk_words) > 50:
            chunks.append(chunk)

        i += chunk_size - overlap

    return chunks
