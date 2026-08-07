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


client = TestClient(app)

USER_EMAIL = "search-test@example.com"
USER_PASSWORD = "uma senha longa e segura"
TEST_JWT_SECRET = (
    "test-only-secret-key-for-textual-search-tests"
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


def get_auth_headers() -> dict[str, str]:
    register_response = client.post(
        "/users",
        json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD,
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}",
    }


def test_search_returns_matching_chunks():
    payload = {
        "title": "Artemis Mission Overview",
        "content": (
            "Artemis is a NASA program focused on returning "
            "humans to the Moon."
        ),
    }

    create_response = client.post(
        "/documents",
        headers=get_auth_headers(),
        json=payload,
    )

    assert create_response.status_code == 201

    document_id = create_response.json()["id"]

    search_response = client.get(
        "/search",
        params={"q": "Moon"},
    )

    assert search_response.status_code == 200

    results = search_response.json()

    assert len(results) == 1
    assert results[0]["document_id"] == document_id
    assert results[0]["document_title"] == payload["title"]
    assert results[0]["content"] == payload["content"]
    assert results[0]["chunk_index"] == 0
    assert results[0]["char_count"] == len(payload["content"])


def test_search_is_case_insensitive():
    payload = {
        "title": "Mars Mission Overview",
        "content": (
            "Mars exploration depends on robotics, orbital data "
            "and mission planning."
        ),
    }

    create_response = client.post(
        "/documents",
        headers=get_auth_headers(),
        json=payload,
    )

    assert create_response.status_code == 201

    search_response = client.get(
        "/search",
        params={"q": "mars"},
    )

    assert search_response.status_code == 200

    results = search_response.json()

    assert len(results) == 1
    assert results[0]["document_title"] == payload["title"]


def test_search_returns_empty_list_when_no_chunks_match():
    payload = {
        "title": "Artemis Mission Overview",
        "content": (
            "Artemis is a NASA program focused on returning "
            "humans to the Moon."
        ),
    }

    create_response = client.post(
        "/documents",
        headers=get_auth_headers(),
        json=payload,
    )

    assert create_response.status_code == 201

    search_response = client.get(
        "/search",
        params={"q": "Jupiter"},
    )

    assert search_response.status_code == 200
    assert search_response.json() == []


def test_search_rejects_blank_query():
    response = client.get(
        "/search",
        params={"q": "   "},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Search query cannot be empty."
    )
