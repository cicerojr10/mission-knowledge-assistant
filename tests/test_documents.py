import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routes.documents import _DOCUMENTS

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_documents():
    _DOCUMENTS.clear()
    yield
    _DOCUMENTS.clear()


def test_create_document_returns_created_document():
    payload = {
        "title": "Artemis Mission Overview",
        "content": "Artemis is a NASA program focused on returning humans to the Moon.",
    }

    response = client.post("/documents", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]


def test_list_documents_returns_created_documents():
    payload = {
        "title": "Artemis Mission Overview",
        "content": "Artemis is a NASA program focused on returning humans to the Moon.",
    }

    client.post("/documents", json=payload)

    response = client.get("/documents")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == payload["title"]
    assert data[0]["content"] == payload["content"]


def test_create_document_rejects_empty_title():
    payload = {
        "title": "   ",
        "content": "Conteúdo válido.",
    }

    response = client.post("/documents", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Document title cannot be empty."


def test_create_document_rejects_empty_content():
    payload = {
        "title": "Documento válido",
        "content": "   ",
    }

    response = client.post("/documents", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Document content cannot be empty."


def test_create_document_rejects_content_too_large():
    payload = {
        "title": "Documento grande",
        "content": "a" * 5001,
    }

    response = client.post("/documents", json=payload)

    assert response.status_code == 413
    assert "Maximum allowed length" in response.json()["detail"]