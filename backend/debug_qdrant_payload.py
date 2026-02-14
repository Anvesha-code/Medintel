from app.db.qdrant_connection import get_qdrant_client, COLLECTION_NAME

client = get_qdrant_client()

points, _ = client.scroll(
    collection_name=COLLECTION_NAME,
    limit=3,
    with_payload=True,
    with_vectors=False
)

print("\n--- QDRANT PAYLOAD CHECK ---\n")

for p in points:
    print("ID:", p.id)
    print("Payload keys:", p.payload.keys())
    print("Payload sample:", {
        "user_id": p.payload.get("user_id"),
        "doc_id": p.payload.get("doc_id"),
        "source_type": p.payload.get("source_type"),
        "text_preview": p.payload.get("text", "")[:100]
    })
    print("-" * 50)
