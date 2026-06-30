from fastapi import FastAPI

from app.config import settings
from app.routes.documents import router as documents_router
from app.routes.health import router as health_router
from app.routes.search import router as search_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API base para o projeto Mission Knowledge Assistant.",
)

app.include_router(health_router)
app.include_router(documents_router)
app.include_router(search_router)
