import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

import app.services.semantic_search as semantic_search_service
from app.database import engine
from app.main import app
from app.models import Chunk, Document
from app.services.embeddings import EMBEDDING_DIMENSION


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_database():
    with Session(engine) as session:
        session.exec(delete(Chunk))
        session.exec(delete(Document))
        session.commit()

    yield

    with Session(engine) as session:
        session.exec(delete(Chunk))
        session.exec(delete(Document))
        session.commit()


def create_vector(
    first_value: float,
    second_value: float = 0.0,
) -> list[float]:
    vector = [0.0] * EMBEDDING_DIMENSION
    vector[0] = first_value
    vector[1] = second_value
    return vector


def create_semantic_search_data() -> None:
    with Session(engine) as session:
        document = Document(
            title="Semantic Search Validation",
            content="Document used to validate semantic search.",
        )
        session.add(document)
        session.flush()

        assert document.id is not None

        chunks = [
            Chunk(
                document_id=document.id,
                content="Exact semantic match.",
                chunk_index=0,
                char_count=len("Exact semantic match."),
                embedding=create_vector(1.0),
            ),
            Chunk(
                document_id=document.id,
                content="Related semantic match.",
                chunk_index=1,
                char_count=len("Related semantic match."),
                embedding=create_vector(0.8, 0.6),
            ),
            Chunk(
                document_id=document.id,
                content="Unrelated semantic content.",
                chunk_index=2,
                char_count=len("Unrelated semantic content."),
                embedding=create_vector(0.0, 1.0),
            ),
            Chunk(
                document_id=document.id,
                content="Chunk without embedding.",
                chunk_index=3,
                char_count=len("Chunk without embedding."),
                embedding=None,
            ),
        ]

        session.add_all(chunks)
        session.commit()


def test_semantic_search_orders_chunks_by_cosine_distance(
    monkeypatch,
):
    query_embedding = create_vector(1.0)

    monkeypatch.setattr(
        semantic_search_service,
        "generate_embedding",
        lambda query: query_embedding,
    )

    create_semantic_search_data()

    response = client.get(
        "/search/semantic",
        params={
            "q": "lunar exploration",
            "top_k": 10,
        },
    )

    assert response.status_code == 200

    results = response.json()

    assert len(results) == 3

    assert [result["content"] for result in results] == [
        "Exact semantic match.",
        "Related semantic match.",
        "Unrelated semantic content.",
    ]

    assert results[0]["distance"] == pytest.approx(
        0.0,
        abs=1e-6,
    )
    assert results[1]["distance"] == pytest.approx(
        0.2,
        abs=1e-6,
    )
    assert results[2]["distance"] == pytest.approx(
        1.0,
        abs=1e-6,
    )


def test_semantic_search_respects_top_k(monkeypatch):
    query_embedding = create_vector(1.0)

    monkeypatch.setattr(
        semantic_search_service,
        "generate_embedding",
        lambda query: query_embedding,
    )

    create_semantic_search_data()

    response = client.get(
        "/search/semantic",
        params={
            "q": "lunar exploration",
            "top_k": 2,
        },
    )

    assert response.status_code == 200

    results = response.json()

    assert len(results) == 2
    assert results[0]["content"] == "Exact semantic match."
    assert results[1]["content"] == "Related semantic match."


def test_semantic_search_rejects_blank_query():
    response = client.get(
        "/search/semantic",
        params={"q": "   "},
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Search query cannot be empty."
    )


@pytest.mark.parametrize("top_k", [0, 21])
def test_semantic_search_validates_top_k(top_k):
    response = client.get(
        "/search/semantic",
        params={
            "q": "lunar exploration",
            "top_k": top_k,
        },
    )

    assert response.status_code == 422