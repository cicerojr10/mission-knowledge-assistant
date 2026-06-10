from fastapi import FastAPI

from app.config import settings
from app.logging_config import configure_logging
from app.routes.documents import router as documents_router
from app.routes.health import router as health_router

configure_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API base para um assistente de IA aplicada com RAG.",
)

app.include_router(health_router)
app.include_router(documents_router)