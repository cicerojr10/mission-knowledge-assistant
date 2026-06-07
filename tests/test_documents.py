from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_document_returns_created_document():
    payload = {
        "title": "Artemis Mission Overview",
        "content": "Artemis is a NASA program focused on returning humans to the Moon.",
    }

    response = client.post("/documents", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]
    assert "id" in data


def test_list_documents_returns_list():
    response = client.get("/documents")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
