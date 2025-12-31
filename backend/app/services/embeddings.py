# app/services/embeddings.py

from sentence_transformers import SentenceTransformer
from typing import List, Dict

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Load embedding model once at startup
        """
        self.model = SentenceTransformer(model_name)

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate vector embedding for a single text chunk
        """
        vector = self.model.encode(text)
        return vector.tolist()

    def generate_embeddings_with_metadata(
        self,
        chunks: List[str],
        doc_id: str,
        source_type: str,
        structured_flag: bool = False
    ) -> List[Dict]:
        """
        Generate embeddings + attach metadata
        """
        records = []
        print("Total chunks:", len(chunks))
        for idx, chunk in enumerate(chunks):
            embedding = self.generate_embedding(chunk)

            record = {
                "embedding": embedding,
                "metadata": {
                    "doc_id": doc_id,
                    "source_type": source_type,
                    "chunk_index": idx,
                    "structured_flag": structured_flag,
                    "text": chunk
                }
            }
            records.append(record)
            print("Embedding dimension:", len(records[0]["embedding"]))

        return records



