from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
from uuid import uuid4
from typing import List, Any
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class VectorStore:
    """
    Thin wrapper around Qdrant client.
    Lazily initializes client and collection.
    """

    def __init__(self):
        self._client = None
        self._collection_initialized = False

        self.collection = settings.QDRANT_COLLECTION
        self.dim = settings.EMBEDDING_DIM  # must exist in settings

    # ---------------------------
    # Internal helpers
    # ---------------------------
    def _get_client(self) -> QdrantClient:
        if self._client is None:
            self._client = QdrantClient(
                url=f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}"
            )
        return self._client

    def _ensure_collection(self):
        if self._collection_initialized:
            return

        client = self._get_client()
        try:
            client.create_collect_
