import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.database import get_session
from app.models import User as UserModel
from app.schemas import UserCreate, UserResponse
from app.services.passwords import hash_password

router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    payload: UserCreate,
    session: Session = Depends(get_session),
):
    normalized_email = str(payload.email)

    existing_user = session.exec(
        select(UserModel).where(
            UserModel.email == normalized_email
        )
    ).first()

    if existing_user is not None:
        logger.warning(
            "Rejected user registration: email already registered"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered.",
        )

    plain_password = payload.password.get_secret_value()

    user = UserModel(
        email=normalized_email,
        password_hash=hash_password(plain_password),
    )

    try:
        session.add(user)
        session.commit()
        session.refresh(user)
    except IntegrityError:
        session.rollback()

        logger.warning(
            "Rejected user registration after database conflict"
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered.",
        )
    except Exception:
        session.rollback()
        logger.exception("Failed to create user")
        raise

    logger.info(
        "User created successfully: id=%s",
        user.id,
    )

    return UserResponse(
        id=str(user.id),
        email=user.email,
    )
