from datetime import datetime, timedelta, timezone

import jwt
from jwt import InvalidTokenError

from app.config import settings


class TokenConfigurationError(RuntimeError):
    """Indica que a configuração necessária para JWT está ausente."""


class InvalidAccessTokenError(ValueError):
    """Indica que um access token é inválido ou expirou."""


def _get_jwt_secret() -> str:
    if settings.jwt_secret_key is None:
        raise TokenConfigurationError(
            "JWT_SECRET_KEY is not configured."
        )

    return settings.jwt_secret_key.get_secret_value()


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Cria um access token JWT para o usuário identificado por subject.
    """
    if not subject:
        raise ValueError("Token subject must not be empty.")

    issued_at = datetime.now(timezone.utc)

    if expires_delta is None:
        expires_delta = timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )

    payload = {
        "sub": subject,
        "iat": issued_at,
        "exp": issued_at + expires_delta,
    }

    return jwt.encode(
        payload,
        _get_jwt_secret(),
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> str:
    """
    Valida um access token e retorna o subject autenticado.
    """
    try:
        payload = jwt.decode(
            token,
            _get_jwt_secret(),
            algorithms=[settings.jwt_algorithm],
            options={
                "require": [
                    "sub",
                    "iat",
                    "exp",
                ]
            },
        )
    except InvalidTokenError as exc:
        raise InvalidAccessTokenError(
            "Invalid or expired access token."
        ) from exc

    subject = payload.get("sub")

    if not isinstance(subject, str) or not subject:
        raise InvalidAccessTokenError(
            "Access token subject is invalid."
        )

    return subject
