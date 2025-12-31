from app.db.qdrant_connection import get_qdrant_client, COLLECTION_NAME

client = get_qdrant_client()

points, _ = client.scroll(
    collection_name=COLLECTION_NAME,
    limit=5
)

for p in points:
    print(p.payload)
