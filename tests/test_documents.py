import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.database import engine
from app.main import app
from app.models import Chunk as ChunkModel
from app.models import Document as DocumentModel

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_documents():
    """
    Limpa chunks e documentos antes e depois de cada teste.

    A tabela chunks possui foreign key para document.
    Por isso, a limpeza direta via SQL precisa remover os chunks antes dos documentos.
    """
    with Session(engine) as session:
        session.exec(delete(ChunkModel))
        session.exec(delete(DocumentModel))
        session.commit()

    yield

    with Session(engine) as session:
        session.exec(delete(ChunkModel))
        session.exec(delete(DocumentModel))
        session.commit()


def test_create_document_returns_created_document_with_chunk_count():
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
    assert data["chunk_count"] == 1


def test_create_document_persists_chunks():
    payload = {
        "title": "Long Artemis Mission Overview",
        "content": "a" * 1200,
    }

    response = client.post("/documents", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["chunk_count"] == 3

    document_id = data["id"]

    chunks_response = client.get(f"/documents/{document_id}/chunks")

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
    response = client.get("/documents/999999/chunks")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found."


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
    assert data[0]["chunk_count"] == 1


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
