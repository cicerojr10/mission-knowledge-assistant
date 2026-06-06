from fastapi import FastAPI

from app.routes.health import router as health_router
from app.routes.documents import router as documents_router
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API base para o projeto Mission Knowledge Assistant.",
)

app.include_router(health_router)
app.include_router(documents_router)
