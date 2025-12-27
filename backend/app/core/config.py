from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str
    env: str
    log_level: str

    database_url: str
    qdrant_url: str

    chunk_size: int
    chunk_overlap: int
    top_k: int

    max_upload_mb: int

    class Config:
        env_file = ".env"

settings = Settings()
