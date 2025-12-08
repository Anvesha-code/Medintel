# app/services/embeddings.py
from sentence_transformers import SentenceTransformer
from typing import List

class Embeddings:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        # Accepts list of texts and returns list of vectors (python lists)
        if not texts:
            return []
        vectors = self.model.encode(texts, show_progress_bar=False)
        # ensure python lists (in case of numpy arrays)
        return [v.tolist() if hasattr(v, "tolist") else v for v in vectors]
