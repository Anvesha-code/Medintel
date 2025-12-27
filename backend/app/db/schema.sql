-- USERS
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DOCUMENTS
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_type TEXT,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    page_count INTEGER,
    sheet_count INTEGER,
    language TEXT,
    extraction_status TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- CHUNKS
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER,
    chunk_index INTEGER,
    chunk_text TEXT,
    source_type TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);

-- EMBEDDINGS METADATA (NO VECTORS YET)
CREATE TABLE IF NOT EXISTS embeddings_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id INTEGER,
    embedding_model TEXT,
    vector_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES chunks(id)
);

-- AUDIO TRANSCRIPTS
CREATE TABLE IF NOT EXISTS media_transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER,
    duration REAL,
    language TEXT,
    transcript_text TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);

-- TABLE METADATA
CREATE TABLE IF NOT EXISTS tables_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER,
    sheet_name TEXT,
    headers TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);
