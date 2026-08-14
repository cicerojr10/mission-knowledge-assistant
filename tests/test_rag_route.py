from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlmodel import Session, delete

from app.config import settings
from app.database import engine
from app.main import app
from app.models import Chunk, Document, User


client = TestClient(app)

USER_PASSWORD = "uma senha longa e segura"
TEST_JWT_SECRET = (
    "test-only-secret-key-for-rag-route-tests"
)


@pytest.fixture(autouse=True)
def configure_test_jwt(monkeypatch):
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
def clear_rag_data():
    with Session(engine) as session:
        session.exec(delete(Chunk))
        session.exec(delete(Document))
        session.exec(delete(User))
        session.commit()

    yield

    with Session(engine) as session:
        session.exec(delete(Chunk))
        session.exec(delete(Document))
        session.exec(delete(User))
        session.commit()


def get_auth_headers() -> dict[str, str]:
    email = f"rag-{uuid4()}@example.com"

    register_response = client.post(
        "/users",
        json={
            "email": email,
            "password": USER_PASSWORD,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": USER_PASSWORD,
        },
    )

    assert login_response.status_code == 200

    return {
        "Authorization": (
            f"Bearer {login_response.json()['access_token']}"
        )
    }


def test_rag_answer_requires_authentication():
    response = client.post(
        "/rag/answer",
        json={
            "question": "What does the document say?",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Could not validate credentials."
    }
    assert response.headers["www-authenticate"] == "Bearer"


def test_rag_answer_abstains_when_no_authorized_context():
    response = client.post(
        "/rag/answer",
        headers=get_auth_headers(),
        json={
            "question": "What does the document say?",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": None,
        "abstained": True,
        "sources": [],
    }
