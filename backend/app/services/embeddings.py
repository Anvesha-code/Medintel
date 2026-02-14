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
        chunks: List[Dict],
        doc_id: int,
        user_id
    ) -> List[Dict]:
        """
        Generate embeddings and attach consistent metadata
        """
        records = []

        print("Total chunks:", len(chunks))

        # ✅ FORCE user_id to STRING (UUID-safe, JWT-safe)
        user_id = str(user_id)

        for idx, chunk_obj in enumerate(chunks):
            text = chunk_obj["text"]
            source_type = chunk_obj["source_type"]

            embedding = self.generate_embedding(text)

            metadata = {
                "user_id": user_id,          # ✅ FIXED
                "doc_id": doc_id,
                "chunk_index": idx,
                "text": text,
                "source_type": source_type
            }

            record = {
                "embedding": embedding,
                "metadata": metadata
            }

            records.append(record)

        print("Embedding dimension:", len(records[0]["embedding"]))
        return records
