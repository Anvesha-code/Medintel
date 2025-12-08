# app/services/chunker.py
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50):
    """
    Splits text into word-based chunks.
    Uses simple overlap to preserve context between chunks.
    """
    if not text:
        return []

    words = text.split()
    if chunk_size <= overlap:
        overlap = 0

    chunks = []
    i = 0
    n = len(words)
    while i < n:
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks
