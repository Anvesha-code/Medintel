from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv
from pathlib import Path
import os

# --------------------------------------------------
# 1️⃣ Explicit .env loading (Windows + Uvicorn safe)
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    print("⚠️ WARNING: .env file not found at", ENV_PATH)

# --------------------------------------------------
# 2️⃣ Settings class (single source of truth)
# --------------------------------------------------
class Settings(BaseSettings):

    # 🔐 Supabase Auth (DEV-SAFE DEFAULTS)
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_JWKS_URL: str = ""

    # 📦 Upload limits
    MAX_UPLOAD_MB: int = 20
    MAX_MEM_READ: int = 20 * 1024 * 1024

    # ✂️ Chunking
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # 🔊 Optional features
    ENABLE_AUDIO: bool = False

    # Pydantic config
    model_config = ConfigDict(
        env_file=str(ENV_PATH),
        extra="allow"   # allow unused env vars safely
    )


# --------------------------------------------------
# 3️⃣ Instantiate settings (WILL NOT CRASH)
# --------------------------------------------------
settings = Settings()

# --------------------------------------------------
# 4️⃣ Runtime validation (CLEAR ERRORS)
# --------------------------------------------------
def validate_settings():
    errors = []

    if not settings.SUPABASE_URL:
        errors.append("SUPABASE_URL")

    if not settings.SUPABASE_ANON_KEY:
        errors.append("SUPABASE_ANON_KEY")

    if not settings.SUPABASE_JWKS_URL:
        errors.append("SUPABASE_JWKS_URL")

    if errors:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(errors)}"
        )

# 🔐 Call validation explicitly
validate_settings()

# --------------------------------------------------
# 5️⃣ Debug (REMOVE AFTER DAY-19)
# --------------------------------------------------
print("✅ ENV FILE PATH:", ENV_PATH)
print("✅ SUPABASE_URL:", settings.SUPABASE_URL)
print("✅ SUPABASE_JWKS_URL:", settings.SUPABASE_JWKS_URL)
