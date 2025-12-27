import sqlite3
from pathlib import Path

DB_PATH = Path("backend/data/medintel.db")
SCHEMA_PATH = Path("app/db/schema.sql")

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
