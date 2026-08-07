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

USER_EMAIL = "documents-test@example.com"
USER_PASSWORD = "uma senha longa e segura"
TEST_JWT_SECRET = (
    "test-only-secret-key-for-document-route-tests"
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


def test_create_document_returns_created_document_with_chunk_count():
    payload = {
        "title": "Artemis Mission Overview",
        "content": (
            "Artemis is a NASA program focused on returning "
            "humans to the Moon."
        ),
    }

    response = client.post(
        "/documents",
        headers=get_auth_headers(),
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]
    assert data["chunk_count"] == 1


def test_create_document_persists_chunks():
    payload = {
        "title": "Long Artemis Mission Overview",
        "content": "a" * 1200,
    }
    auth_headers = get_auth_headers()

    response = client.post(
        "/documents",
        headers=auth_headers,
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["chunk_count"] == 3

    document_id = data["id"]

    chunks_response = client.get(
        f"/documents/{document_id}/chunks",
        headers=auth_headers,
    )

    assert chunks_response.status_code == 200

    chunks = chunks_response.json()

    assert len(chunks) == 3

    assert chunks[0]["document_id"] == document_id
    assert chunks[0]["chunk_index"] == 0
    assert chunks[0]["char_count"] == 500

    assert chunks[1]["document_id"] == document_id
    assert chunks[1]["chunk_index"] == 1
    assert chunks[1]["char_count"] == 500

    assert chunks[2]["document_id"] == document_id
    assert chunks[2]["chunk_index"] == 2
    assert chunks[2]["char_count"] == 300


def test_list_document_chunks_returns_not_found_for_missing_document():
    response = client.get(
        "/documents/999999/chunks",
        headers=get_auth_headers(),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found."


def test_list_documents_returns_created_documents():
    payload = {
        "title": "Artemis Mission Overview",
        "content": (
            "Artemis is a NASA program focused on returning "
            "humans to the Moon."
        ),
    }
    auth_headers = get_auth_headers()

    create_response = client.post(
        "/documents",
        headers=auth_headers,
        json=payload,
    )

    assert create_response.status_code == 201

    response = client.get(
        "/documents",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == payload["title"]
    assert data[0]["content"] == payload["content"]
    assert data[0]["chunk_count"] == 1


def test_create_document_rejects_empty_title():
    payload = {
        "title": "   ",
        "content": "Conteúdo válido.",
    }

    response = client.post(
        "/documents",
        headers=get_auth_headers(),
        json=payload,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Document title cannot be empty."
    )


def test_create_document_rejects_empty_content():
    payload = {
        "title": "Documento válido",
        "content": "   ",
    }

    response = client.post(
        "/documents",
        headers=get_auth_headers(),
        json=payload,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Document content cannot be empty."
    )


def test_create_document_rejects_content_too_large():
    payload = {
        "title": "Documento grande",
        "content": "a" * 5001,
    }

    response = client.post(
        "/documents",
        headers=get_auth_headers(),
        json=payload,
    )

    assert response.status_code == 413
    assert "Maximum allowed length" in response.json()["detail"]
