from pydantic import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "MedIntel"
    ENV: str = "local"

    # Upload
    MAX_UPLOAD_MB: int = 20
    MAX_MEM_READ: int = 20 * 1024 * 1024

    # Chunking
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # Audio
    ENABLE_AUDIO: bool = False
    AUDIO_CHUNK_CHARS: int = 1500
    AUDIO_CHUNK_OVERLAP: int = 100
    WHISPER_MODEL: str = "small"

    # Vector DB
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "medintel_vectors"

    class Config:
        env_file = ".env"

settings = Settings()
