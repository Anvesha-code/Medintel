from app.services.vector_store import store_embedding

# Dummy test data
dummy_embeddings = [
    [0.01] * 384,
    [0.02] * 384
]

dummy_metadatas = [
    {
        "id": "doc1_chunk_0",
        "document_id": "doc1",
        "user_id": "user_001",
        "chunk_index": 0,
        "source_type": "pdf",
        "language": "en",
        "structured_flag": False
    },
    {
        "id": "doc1_chunk_1",
        "document_id": "doc1",
        "user_id": "user_001",
        "chunk_index": 1,
        "source_type": "pdf",
        "language": "en",
        "structured_flag": False
    }
]

store_embedding(dummy_embeddings, dummy_metadatas)
print("Embeddings stored successfully")
