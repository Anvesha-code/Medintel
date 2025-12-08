# app/services/vector_store.py
from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
from uuid import uuid4
from typing import List, Any
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class VectorStore:
    def __init__(self, host="localhost", port=6333, collection="medintel_vectors", dim=384):
        self.collection = collection
        self.dim = dim
        self.client = QdrantClient(url=f"http://{host}:{port}")

        # Try to create collection (non-destructive if already exists)
        try:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=qm.VectorParams(size=self.dim, distance=qm.Distance.COSINE)
            )
            logger.info("Collection created (or already exists).")
        except Exception as e:
            logger.debug("create_collection error (may already exist): %s", e)

    def insert_vectors(self, vectors: List[List[float]], payloads: List[dict]):
        points = []
        for vec, pay in zip(vectors, payloads):
            points.append(
                qm.PointStruct(
                    id=str(uuid4()),
                    vector=vec,
                    payload=pay
                )
            )
        try:
            self.client.upsert(collection_name=self.collection, points=points)
            logger.info("Upserted %d points into '%s'.", len(points), self.collection)
        except Exception as e:
            logger.error("Error upserting points: %s", e)
            raise

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Any]:
        """
        Robust search wrapper for the qdrant client you have (uses query_points with 'query' kw).
        Returns raw results (list) or [] on error.
        """
        try:
            client = self.client
            coll = self.collection

            # 1) If client supports query_points, call it with `query=` (this matches your client)
            if hasattr(client, "query_points"):
                try:
                    resp = client.query_points(
                        collection_name=coll,
                        query=query_vector,  # <- important: use `query` kw
                        limit=top_k,
                        with_payload=True,  # include payload so you can read "text"
                        with_vectors=False
                    )
                    # resp may be QueryResponse or similar; try to return .points or the response itself
                    return getattr(resp, "points", resp) or []
                except TypeError as e:
                    # If kwargs fail, attempt a positional call as fallback
                    try:
                        resp = client.query_points(coll, query_vector, top_k)
                        return getattr(resp, "points", resp) or []
                    except Exception:
                        logger.error("query_points fallback failed: %s", e)

            # 2) Try other candidate methods (defensive)
            if hasattr(client, "search"):
                try:
                    return client.search(collection_name=coll, query_vector=query_vector, limit=top_k)
                except Exception:
                    try:
                        return client.search(collection_name=coll, vector=query_vector, limit=top_k)
                    except Exception:
                        pass

            if hasattr(client, "search_points"):
                try:
                    return client.search_points(collection_name=coll, vector=query_vector, limit=top_k)
                except Exception:
                    try:
                        return client.search_points(collection_name=coll, query_vector=query_vector, limit=top_k)
                    except Exception:
                        pass

            logger.error("No usable search/query method found on qdrant client.")
            return []
        except Exception as e:
            logger.error("Qdrant search error: %s", e)
            return []
