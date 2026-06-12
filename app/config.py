import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "Mission Knowledge Assistant")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    environment: str = os.getenv("APP_ENV", "local")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    max_document_content_length: int = int(
        os.getenv("MAX_DOCUMENT_CONTENT_LENGTH", "5000")
    )


settings = Settings()