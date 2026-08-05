from typing import NoReturn

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlmodel import Session

from app.database import get_session
from app.models import User as UserModel
from app.services.tokens import (
    InvalidAccessTokenError,
    decode_access_token,
)


bearer_scheme = HTTPBearer(auto_error=False)


def raise_credentials_exception() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    session: Session = Depends(get_session),
) -> UserModel:
    """
    Resolve o usuário autenticado a partir do access token Bearer.
    """
    if credentials is None:
        raise_credentials_exception()

    try:
        subject = decode_access_token(
            credentials.credentials
        )
        user_id = int(subject)
    except (InvalidAccessTokenError, ValueError):
        raise_credentials_exception()

    user = session.get(UserModel, user_id)

    if user is None:
        raise_credentials_exception()

    return user
