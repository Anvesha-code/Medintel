from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import socket

# -------------------------------
# CONFIG
# -------------------------------
QDRANT_HOST = "127.0.0.1"
QDRANT_PORT = 6333
QDRANT_URL = f"http://{QDRANT_HOST}:{QDRANT_PORT}"

COLLECTION_NAME = "medintel_chunk"
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2


# -------------------------------
# CLIENT CREATION (RAG SAFE)
# -------------------------------
def get_qdrant_client() -> QdrantClient:
    # Hard check: Qdrant must be reachable
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((QDRANT_HOST, QDRANT_PORT))
    sock.close()

    if result != 0:
        raise RuntimeError("❌ Qdrant server is NOT running on port 6333")

    print("✅ Qdrant server detected (REST MODE, RAG SAFE)")

    # ✅ REST client ONLY (NO MATRIX MODE)
    return QdrantClient(
        url=QDRANT_URL,
        timeout=60,
        prefer_grpc=False
    )


# -------------------------------
# COLLECTION SETUP
# -------------------------------
def create_collection_if_not_exists():
    client = get_qdrant_client()

    existing = client.get_collections().collections
    if any(col.name == COLLECTION_NAME for col in existing):
        print("✅ Qdrant collection already exists")
        return

    print("🛠️ Creating Qdrant collection:", COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=EMBEDDING_DIM,
            distance=Distance.COSINE
        )
    )

    print("✅ Qdrant collection created successfully")


# -------------------------------
# ENTRY POINT
# -------------------------------
if __name__ == "__main__":
    create_collection_if_not_exists()
