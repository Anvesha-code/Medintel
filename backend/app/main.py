from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes_upload import router as upload_router
from app.api.routes_chat import router as chat_router
from app.api.routes_health import router as health_router
from app.api.routes_documents import router as documents_router
from app.db.init_db import init_db

app = FastAPI(title="Medintel API",version="0.1.0")
# CORS settings -
origins = [
    "http://localhost:8501",      # Streamlit default
    "http://127.0.0.1:8501",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "*"                           # during development – we can restrict later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(upload_router, prefix="/files")
app.include_router(chat_router, prefix="/chat")
app.include_router(documents_router)
app.include_router(health_router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
async def root():
    return {"message": "MedIntel backend is running"}