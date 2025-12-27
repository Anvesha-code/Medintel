import sqlite3

conn = sqlite3.connect("backend/data/medintel.db")
cursor = conn.cursor()

tables = ["users", "documents", "chunks", "embeddings_metadata"]

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table};")
    count = cursor.fetchone()[0]
    print(f"{table}: {count} rows")

conn.close()
