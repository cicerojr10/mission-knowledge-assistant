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
    Por isso, chunks precisam ser removidos antes de document.
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


def test_search_returns_matching_chunks():
    payload = {
        "title": "Artemis Mission Overview",
        "content": "Artemis is a NASA program focused on returning humans to the Moon.",
    }

    create_response = client.post("/documents", json=payload)

    assert create_response.status_code == 201

    document_id = create_response.json()["id"]

    search_response = client.get("/search", params={"q": "Moon"})

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
        "content": "Mars exploration depends on robotics, orbital data and mission planning.",
    }

    create_response = client.post("/documents", json=payload)

    assert create_response.status_code == 201

    search_response = client.get("/search", params={"q": "mars"})

    assert search_response.status_code == 200

    results = search_response.json()

    assert len(results) == 1
    assert results[0]["document_title"] == payload["title"]


def test_search_returns_empty_list_when_no_chunks_match():
    payload = {
        "title": "Artemis Mission Overview",
        "content": "Artemis is a NASA program focused on returning humans to the Moon.",
    }

    create_response = client.post("/documents", json=payload)

    assert create_response.status_code == 201

    search_response = client.get("/search", params={"q": "Jupiter"})

    assert search_response.status_code == 200
    assert search_response.json() == []


def test_search_rejects_blank_query():
    response = client.get("/search", params={"q": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Search query cannot be empty."
