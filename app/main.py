from fastapi import FastAPI

from app.config import settings
from app.routes.health import router as health_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API base para um assistente de IA aplicada com RAG."
)

app.include_router(health_router)