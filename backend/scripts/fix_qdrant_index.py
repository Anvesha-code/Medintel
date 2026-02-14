from app.db.qdrant_connection import get_qdrant_client, COLLECTION_NAME

client = get_qdrant_client()

client.update_collection(
    collection_name=COLLECTION_NAME,
    optimizer_config={
        "indexing_threshold": 1
    }
)

print("✅ Qdrant indexing_threshold set to 1")
