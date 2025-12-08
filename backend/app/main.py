from fastapi import FastAPI
from app.api.routes_upload import router as upload_router
from app.api.routes_chat import router as chat_router



app = FastAPI()
app.include_router(upload_router, prefix="/files")
app.include_router(chat_router, prefix="/chat")
