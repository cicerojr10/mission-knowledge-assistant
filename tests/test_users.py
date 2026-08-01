import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete, select

from app.database import engine
from app.main import app
from app.models import Chunk as ChunkModel
from app.models import Document as DocumentModel
from app.models import User as UserModel
from app.services.passwords import verify_password

client = TestClient(app)

VALID_PASSWORD = "uma senha longa e segura"


@pytest.fixture(autouse=True)
def clear_users_and_documents():
    """
    Limpa os dados respeitando a ordem das foreign keys.
    """
    with Session(engine) as session:
        session.exec(delete(ChunkModel))
        session.exec(delete(DocumentModel))
        session.exec(delete(UserModel))
        session.commit()

    yield

    with Session(engine) as session:
        session.exec(delete(ChunkModel))
        session.exec(delete(DocumentModel))
        session.exec(delete(UserModel))
        session.commit()


def test_create_user_returns_normalized_email_without_password_fields():
    response = client.post(
        "/users",
        json={
            "email": "  Cicero@Example.COM  ",
            "password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert set(data.keys()) == {"id", "email"}
    assert data["email"] == "cicero@example.com"
    assert "password" not in data
    assert "password_hash" not in data


def test_create_user_persists_argon2_hash_instead_of_plaintext():
    password_with_spaces = " uma senha bem segura "

    response = client.post(
        "/users",
        json={
            "email": "user@example.com",
            "password": password_with_spaces,
        },
    )

    assert response.status_code == 201

    with Session(engine) as session:
        user = session.exec(
            select(UserModel).where(
                UserModel.email == "user@example.com"
            )
        ).first()

        assert user is not None
        assert user.password_hash != password_with_spaces
        assert user.password_hash.startswith("$argon2id$")
        assert verify_password(
            password_with_spaces,
            user.password_hash,
        ) is True
        assert verify_password(
            password_with_spaces.strip(),
            user.password_hash,
        ) is False


def test_create_user_rejects_duplicate_normalized_email():
    first_response = client.post(
        "/users",
        json={
            "email": "Cicero@Example.COM",
            "password": VALID_PASSWORD,
        },
    )

    second_response = client.post(
        "/users",
        json={
            "email": "cicero@example.com",
            "password": "outra senha longa e segura",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Email is already registered."
    }


def test_create_user_rejects_invalid_email():
    response = client.post(
        "/users",
        json={
            "email": "not-an-email",
            "password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 422


def test_create_user_rejects_short_password():
    response = client.post(
        "/users",
        json={
            "email": "user@example.com",
            "password": "a" * 14,
        },
    )

    assert response.status_code == 422
