from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    MAX_UPLOAD_MB: int = 20
    MAX_MEM_READ: int = 20 * 1024 * 1024

    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    ENABLE_AUDIO: bool = False

    # 🔑 THIS IS THE FIX
    model_config = ConfigDict(
        env_file=".env",
        extra="allow"   # <-- allow unused env vars
    )

settings = Settings()
