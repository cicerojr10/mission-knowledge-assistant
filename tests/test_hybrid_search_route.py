import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

import app.routes.search as search_route
from app.main import app
from app.models import Chunk, Document
from app.services.hybrid_search import HybridSearchResult


client = TestClient(app)


def create_hybrid_result() -> HybridSearchResult:
    document = Document(
        id=20,
        title="Artemis Program",
        content=(
            "The Artemis program will return "
            "astronauts to the Moon."
        ),
    )

    chunk = Chunk(
        id=10,
        document_id=20,
        content=document.content,
        chunk_index=0,
        char_count=len(document.content),
        embedding=None,
    )

    return HybridSearchResult(
        chunk=chunk,
        document=document,
        rrf_score=(1 / 61) + (1 / 61),
        textual_rank=1,
        semantic_rank=1,
        semantic_distance=0.20,
    )


def test_hybrid_search_uses_default_parameters(
    monkeypatch,
):
    received_arguments = {}

    def fake_hybrid_search(
        session: Session,
        query: str,
        top_k: int,
        max_distance: float | None = None,
        rrf_k: int = 60,
    ):
        received_arguments["query"] = query
        received_arguments["top_k"] = top_k
        received_arguments["max_distance"] = (
            max_distance
        )
        received_arguments["rrf_k"] = rrf_k

        return []

    monkeypatch.setattr(
        search_route,
        "search_chunks_hybrid",
        fake_hybrid_search,
    )

    response = client.get(
        "/search/hybrid",
        params={
            "q": "Artemis",
        },
    )

    assert response.status_code == 200
    assert response.json() == []

    assert received_arguments == {
        "query": "Artemis",
        "top_k": 5,
        "max_distance": None,
        "rrf_k": 60,
    }


def test_hybrid_search_serializes_result_and_forwards_parameters(
    monkeypatch,
):
    received_arguments = {}

    def fake_hybrid_search(
        session: Session,
        query: str,
        top_k: int,
        max_distance: float | None = None,
        rrf_k: int = 60,
    ):
        received_arguments["query"] = query
        received_arguments["top_k"] = top_k
        received_arguments["max_distance"] = (
            max_distance
        )
        received_arguments["rrf_k"] = rrf_k

        return [
            create_hybrid_result()
        ]

    monkeypatch.setattr(
        search_route,
        "search_chunks_hybrid",
        fake_hybrid_search,
    )

    response = client.get(
        "/search/hybrid",
        params={
            "q": "return to the Moon",
            "top_k": 3,
            "max_distance": 0.60,
            "rrf_k": 30,
        },
    )

    assert response.status_code == 200

    results = response.json()

    assert len(results) == 1

    result = results[0]

    assert result["chunk_id"] == "10"
    assert result["document_id"] == "20"
    assert result["document_title"] == (
        "Artemis Program"
    )
    assert result["content"] == (
        "The Artemis program will return "
        "astronauts to the Moon."
    )
    assert result["chunk_index"] == 0
    assert result["char_count"] == 55
    assert result["rrf_score"] == pytest.approx(
        (1 / 61) + (1 / 61)
    )
    assert result["textual_rank"] == 1
    assert result["semantic_rank"] == 1
    assert result["semantic_distance"] == pytest.approx(
        0.20
    )

    assert received_arguments == {
        "query": "return to the Moon",
        "top_k": 3,
        "max_distance": 0.60,
        "rrf_k": 30,
    }


def test_hybrid_search_rejects_blank_query():
    response = client.get(
        "/search/hybrid",
        params={
            "q": "   ",
        },
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": "Search query cannot be empty.",
    }


@pytest.mark.parametrize(
    "top_k",
    [0, 21],
)
def test_hybrid_search_validates_top_k(
    top_k,
):
    response = client.get(
        "/search/hybrid",
        params={
            "q": "Artemis",
            "top_k": top_k,
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "max_distance",
    [-0.01, 2.01],
)
def test_hybrid_search_validates_max_distance(
    max_distance,
):
    response = client.get(
        "/search/hybrid",
        params={
            "q": "Artemis",
            "max_distance": max_distance,
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "rrf_k",
    [0, 1001],
)
def test_hybrid_search_validates_rrf_k(
    rrf_k,
):
    response = client.get(
        "/search/hybrid",
        params={
            "q": "Artemis",
            "rrf_k": rrf_k,
        },
    )

    assert response.status_code == 422