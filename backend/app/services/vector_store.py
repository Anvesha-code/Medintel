from typing import List, Dict
from uuid import uuid4
from qdrant_client.models import PointStruct
from app.db.qdrant_connection import (
    get_qdrant_client,
    COLLECTION_NAME
)


class VectorStore:
    """
    Handles all interactions with Qdrant:
    - Storing vectors
    - Searching vectors

    Qdrant is used in SERVER MODE.
    """

    def __init__(self):
        self.client = get_qdrant_client()
        self.collection_name = COLLECTION_NAME

        # Debug: confirm available server search methods
        print(
            "QDRANT SEARCH METHODS:",
            [m for m in dir(self.client) if "search" in m]
        )

    # --------------------------------------------------
    # STORE VECTORS
    # --------------------------------------------------
    def store(self, records: list):
        """
        records = [
            {
                "embedding": [...],
                "metadata": {
                    "doc_id": int,
                    "chunk_index": int,
                    "text": str,
                    "source_type": str,
                    "filename": str
                }
            }
        ]
        """

        if not records:
            return

        points = []

        for record in records:
            embedding = record["embedding"]
            metadata = record["metadata"]

            point = PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "doc_id": metadata["doc_id"],
                    "chunk_index": metadata["chunk_index"],
                    "text": metadata["text"],
                    "source_type": metadata.get("source_type"),
                    "filename": metadata.get("filename"),
                }
            )

            points.append(point)

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        print(f"✅ Stored {len(points)} vectors in Qdrant")

    # --------------------------------------------------
    # SEARCH VECTORS (QDRANT SERVER MODE)
    # --------------------------------------------------

    # ✅ SEARCH MUST BE INSIDE CLASS

    def search(self, query_embedding, top_k=5):
        print("🔍 Calling Qdrant search (RAG SAFE)")

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            with_payload=True
        )

        matches = []
        for point in results:
            matches.append({
                "id": point.id,
                "score": point.score,
                "text": point.payload.get("text"),
                "filename": point.payload.get("filename"),
                "chunk_index": point.payload.get("chunk_index"),
                "doc_id": point.payload.get("doc_id")
            })

        return matches
