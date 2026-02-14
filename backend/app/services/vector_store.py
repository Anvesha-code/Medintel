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
    - Deleting vectors (re-embedding safe)
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
                    "user_id": str(metadata["user_id"]),  # ✅ FORCE STRING
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

        print(f"Stored {len(points)} vectors in Qdrant")

    # --------------------------------------------------
    # DELETE VECTORS BY DOCUMENT (CRITICAL FIX)
    # --------------------------------------------------
    def delete_by_document(self, user_id: str, document_id: int):
        """
        Deletes all vectors for a given user + document
        Used before re-embedding
        """
        print(
            f"Deleting Qdrant vectors for user_id={user_id}, document_id={document_id}"
        )

        delete_filter = Filter(
            must=[
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=str(user_id))
                ),
                FieldCondition(
                    key="doc_id",
                    match=MatchValue(value=document_id)
                )
            ]
        )

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=delete_filter
        )

        print("Old embeddings deleted successfully")

    # --------------------------------------------------
    # SEARCH VECTORS
    # --------------------------------------------------
    def search(
        self,
        query_embedding,
        user_id: str,
        document_id: int | None = None,
        source_type: str | None = None,
        top_k: int = 5
    ):
        print("SEARCH CALLED")
        print("  user_id:", user_id)
        print("  document_id:", document_id)
        print("  source_type:", source_type)
        print("  top_k:", top_k)

        must_conditions = [
            FieldCondition(
                key="user_id",
                match=MatchValue(value=str(user_id))
            )
        ]

        if document_id:
            must_conditions.append(
                FieldCondition(
                    key="doc_id",
                    match=MatchValue(value=document_id)
                )
            )

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
            query_filter=search_filter
        )

        print("QDRANT RESULTS:", len(results))

        # 🔴 DEBUG EACH RESULT
        for r in results:
            print("---- RESULT ----")
            print("Score:", r.score)
            print("User ID:", r.payload.get("user_id"))
            print("Doc ID:", r.payload.get("doc_id"))
            print("Text Preview:", r.payload.get("text", "")[:150])

        return results
