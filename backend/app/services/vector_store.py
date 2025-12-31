from typing import List, Dict
from uuid import uuid4
from qdrant_client.models import PointStruct
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.db.qdrant_connection import (
    get_qdrant_client,
    COLLECTION_NAME
)


class VectorStore:
    """
    Handles all interactions with Qdrant:
    - Storing vectors
    - Searching vectors
    """

    def __init__(self):
        self.client = get_qdrant_client()
        self.collection_name = COLLECTION_NAME

        print(
            "QDRANT SEARCH METHODS:",
            [m for m in dir(self.client) if "search" in m]
        )

    # --------------------------------------------------
    # STORE VECTORS
    # --------------------------------------------------
    def store(self, records: List[Dict]):
        if not records:
            return

        points = []

        for record in records:
            metadata = record["metadata"]

            point = PointStruct(
                id=str(uuid4()),
                vector=record["embedding"],
                payload={
                    "user_id": metadata["user_id"],
                    "doc_id": metadata["doc_id"],
                    "chunk_index": metadata["chunk_index"],
                    "text": metadata["text"],
                    "source_type": metadata["source_type"]
                }
            )
            points.append(point)

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        print(f"✅ Stored {len(points)} vectors in Qdrant")

    # --------------------------------------------------
    # SEARCH VECTORS (SAFE DAY-9 VERSION)
    # --------------------------------------------------
    def search(
        self,
        query_embedding,
        user_id: str,
        source_type: str | None = None,
        top_k: int = 5
    ):
        print("🔍 SEARCH CALLED")
        print("   user_id:", user_id)
        print("   source_type:", source_type)
        print("   top_k:", top_k)

        # always filter by user
        must_conditions = [
            FieldCondition(
                key="user_id",
                match=MatchValue(value=user_id)
            )
        ]

        # filter by source_type ONLY if provided
        if source_type:
            must_conditions.append(
                FieldCondition(
                    key="source_type",
                    match=MatchValue(value=source_type)
                )
            )

        search_filter = Filter(must=must_conditions)

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            #query_filter=search_filter
        )

        print("🧲 QDRANT RESULTS:", len(results))
        return results
