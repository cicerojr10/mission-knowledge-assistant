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

USER_EMAIL = "document-owner@example.com"
USER_PASSWORD = "uma senha longa e segura"
TEST_JWT_SECRET = (
    "test-only-secret-key-for-document-authorization-tests"
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
def clear_security_data():
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


def register_and_login_user() -> tuple[dict, dict[str, str]]:
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

    return (
        register_response.json(),
        {
            "Authorization": f"Bearer {access_token}",
        },
    )


def test_create_document_rejects_missing_token():
    response = client.post(
        "/documents",
        json={
            "title": "Documento privado",
            "content": "Conteúdo pertencente ao usuário autenticado.",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Could not validate credentials."
    }
    assert response.headers["www-authenticate"] == "Bearer"


def test_create_document_assigns_authenticated_user_as_owner():
    registered_user, auth_headers = register_and_login_user()

    response = client.post(
        "/documents",
        headers=auth_headers,
        json={
            "title": "Documento do proprietário",
            "content": "Conteúdo privado do usuário autenticado.",
        },
    )

    assert response.status_code == 201

    document_id = int(response.json()["id"])

    with Session(engine) as session:
        document = session.get(DocumentModel, document_id)

        assert document is not None
        assert document.owner_id == int(registered_user["id"])

def test_list_documents_rejects_missing_token():
    response = client.get("/documents")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Could not validate credentials."
    }
    assert response.headers["www-authenticate"] == "Bearer"


def get_auth_headers_for_user(email: str) -> dict[str, str]:
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

    access_token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}",
    }


def test_list_documents_returns_only_authenticated_user_documents():
    first_user_headers = get_auth_headers_for_user(
        "first-document-owner@example.com"
    )
    second_user_headers = get_auth_headers_for_user(
        "second-document-owner@example.com"
    )

    first_response = client.post(
        "/documents",
        headers=first_user_headers,
        json={
            "title": "Documento do primeiro usuário",
            "content": "Conteúdo privado do primeiro usuário.",
        },
    )
    second_response = client.post(
        "/documents",
        headers=second_user_headers,
        json={
            "title": "Documento do segundo usuário",
            "content": "Conteúdo privado do segundo usuário.",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    response = client.get(
        "/documents",
        headers=first_user_headers,
    )

    assert response.status_code == 200

    documents = response.json()

    assert len(documents) == 1
    assert documents[0]["id"] == first_response.json()["id"]
    assert documents[0]["title"] == (
        "Documento do primeiro usuário"
    )




def test_list_document_chunks_rejects_missing_token():
    response = client.get("/documents/999999/chunks")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Could not validate credentials."
    }
    assert response.headers["www-authenticate"] == "Bearer"


def test_list_document_chunks_hides_other_user_document():
    owner_headers = get_auth_headers_for_user(
        "chunk-owner@example.com"
    )
    other_user_headers = get_auth_headers_for_user(
        "other-chunk-user@example.com"
    )

    create_response = client.post(
        "/documents",
        headers=owner_headers,
        json={
            "title": "Documento privado com chunks",
            "content": "Conteúdo privado pertencente ao proprietário.",
        },
    )

    assert create_response.status_code == 201

    document_id = create_response.json()["id"]

    response = client.get(
        f"/documents/{document_id}/chunks",
        headers=other_user_headers,
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document not found."
    }
