import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlmodel import Session, delete

from app.config import settings
from app.database import engine
from app.main import app
from app.models import Chunk as ChunkModel
from app.models import Document as DocumentModel
from app.models import User as UserModel
from app.services.tokens import (
    create_access_token,
    decode_access_token,
)


client = TestClient(app)

USER_EMAIL = "user@example.com"
USER_PASSWORD = "uma senha longa e segura"
TEST_JWT_SECRET = (
    "test-only-secret-key-for-authentication-route-tests"
)


@pytest.fixture(autouse=True)
def configure_test_jwt(monkeypatch):
    """
    Mantém os testes independentes do arquivo .env local.
    """
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        SecretStr(TEST_JWT_SECRET),
    )
    monkeypatch.setattr(
        settings,
        "jwt_algorithm",
        "HS256",
    )
    monkeypatch.setattr(
        settings,
        "jwt_access_token_expire_minutes",
        30,
    )


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


def register_test_user() -> dict:
    response = client.post(
        "/users",
        json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD,
        },
    )

    assert response.status_code == 201

    return response.json()


def login_test_user() -> tuple[dict, str]:
    registered_user = register_test_user()

    response = client.post(
        "/auth/login",
        json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD,
        },
    )

    assert response.status_code == 200

    return (
        registered_user,
        response.json()["access_token"],
    )


def assert_invalid_token_response(response) -> None:
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Could not validate credentials."
    }
    assert response.headers["www-authenticate"] == "Bearer"


def assert_invalid_credentials_response(response) -> None:
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid email or password."
    }
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_returns_bearer_token_for_valid_credentials():
    registered_user = register_test_user()

    response = client.post(
        "/auth/login",
        json={
            "email": "  User@Example.COM  ",
            "password": USER_PASSWORD,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert set(data.keys()) == {
        "access_token",
        "token_type",
    }
    assert data["token_type"] == "bearer"
    assert (
        decode_access_token(data["access_token"])
        == registered_user["id"]
    )


def test_login_rejects_wrong_password():
    register_test_user()

    response = client.post(
        "/auth/login",
        json={
            "email": USER_EMAIL,
            "password": "uma senha incorreta e longa",
        },
    )

    assert_invalid_credentials_response(response)


def test_login_rejects_unknown_email():
    response = client.post(
        "/auth/login",
        json={
            "email": "missing@example.com",
            "password": USER_PASSWORD,
        },
    )

    assert_invalid_credentials_response(response)


def test_read_current_user_returns_authenticated_user():
    registered_user, access_token = login_test_user()

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": registered_user["id"],
        "email": USER_EMAIL,
    }


def test_read_current_user_rejects_missing_token():
    response = client.get("/auth/me")

    assert_invalid_token_response(response)


def test_read_current_user_rejects_tampered_token():
    _, access_token = login_test_user()

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": (
                f"Bearer {access_token}tampered"
            ),
        },
    )

    assert_invalid_token_response(response)


def test_read_current_user_rejects_unknown_user_subject():
    access_token = create_access_token(
        subject="999999999"
    )

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert_invalid_token_response(response)
