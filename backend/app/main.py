# =========================
# LOAD ENV FIRST (CRITICAL)
# =========================
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env from backend/app/.env
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Debug check (safe to keep in dev)
print("OPENAI_API_KEY LOADED:", bool(os.getenv("OPENAI_API_KEY")))
print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("SUPABASE_JWKS_URL:", os.getenv("SUPABASE_JWKS_URL"))

# =========================
# NOW IMPORT THE APP
# =========================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_upload import router as upload_router
from app.api.routes_chat import router as chat_router
from app.api.routes_health import router as health_router
from app.api.routes_documents import router as documents_router

from app.db.init_db import init_db

# =========================
# FASTAPI APP
# =========================
app = FastAPI(
    title="Medintel API",
    version="0.1.0"
)

# =========================
# CORS CONFIG
# =========================
origins = [
    "http://localhost:8501",
    "http://127.0.0.1:8501"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROUTERS
# =========================
app.include_router(upload_router, prefix="/files")
app.include_router(chat_router, prefix="/chat")
app.include_router(documents_router)
app.include_router(health_router)

# =========================
# STARTUP
# =========================
@app.on_event("startup")
def on_startup():
    init_db()

# =========================
# ROOT
# =========================
@app.get("/")
async def root():
    return {"message": "MedIntel backend is running"}
