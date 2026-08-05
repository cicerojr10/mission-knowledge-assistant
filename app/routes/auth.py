import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies.auth import get_current_user
from app.models import User as UserModel
from app.schemas import (
    LoginRequest,
    TokenResponse,
    UserResponse,
)
from app.services.passwords import verify_password
from app.services.tokens import create_access_token


router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


def raise_invalid_credentials() -> None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    payload: LoginRequest,
    session: Session = Depends(get_session),
) -> TokenResponse:
    normalized_email = str(payload.email)

    user = session.exec(
        select(UserModel).where(
            UserModel.email == normalized_email
        )
    ).first()

    if user is None:
        logger.warning(
            "Rejected login attempt: invalid credentials"
        )
        raise_invalid_credentials()

    plain_password = payload.password.get_secret_value()

    if not verify_password(
        plain_password,
        user.password_hash,
    ):
        logger.warning(
            "Rejected login attempt: invalid credentials"
        )
        raise_invalid_credentials()

    if user.id is None:
        raise RuntimeError(
            "Authenticated user does not have a persisted ID."
        )

    access_token = create_access_token(
        subject=str(user.id)
    )

    logger.info(
        "User authenticated successfully: id=%s",
        user.id,
    )

    return TokenResponse(
        access_token=access_token,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def read_current_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserResponse:
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
    )
