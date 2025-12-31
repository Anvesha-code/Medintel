from app.db.qdrant_connection import get_qdrant_client

client = get_qdrant_client()

print("CLIENT TYPE:", type(client))
print("COLLECTIONS:", client.get_collections())
print("POINT COUNT:", client.count(collection_name="medintel_chunks", exact=True))
