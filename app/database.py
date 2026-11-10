import os
from collections.abc import Generator

from sqlmodel import Session, create_engine


DEFAULT_DATABASE_URL = (
    "postgresql://mission_user:mission_password"
    "@localhost:5432/mission_knowledge"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    DEFAULT_DATABASE_URL,
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session