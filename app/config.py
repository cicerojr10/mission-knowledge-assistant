import os
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr


load_dotenv()


def get_optional_secret(environment_variable: str) -> SecretStr | None:
    value = os.getenv(environment_variable)

    if not value:
        return None

    return SecretStr(value)


class Settings(BaseModel):
    app_name: str = os.getenv(
        "APP_NAME",
        "Mission Knowledge Assistant",
    )
    app_version: str = os.getenv(
        "APP_VERSION",
        "0.1.0",
    )
    environment: str = os.getenv(
        "APP_ENV",
        "local",
    )
    log_level: str = os.getenv(
        "LOG_LEVEL",
        "INFO",
    )
    max_document_content_length: int = int(
        os.getenv(
            "MAX_DOCUMENT_CONTENT_LENGTH",
            "5000",
        )
    )

    jwt_secret_key: SecretStr | None = get_optional_secret(
        "JWT_SECRET_KEY"
    )
    jwt_algorithm: Literal["HS256"] = os.getenv(
        "JWT_ALGORITHM",
        "HS256",
    )
    jwt_access_token_expire_minutes: int = Field(
        default=int(
            os.getenv(
                "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
                "30",
            )
        ),
        gt=0,
        le=1440,
    )


settings = Settings()