from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

import app.routes.search as search_route
import app.services.semantic_search as semantic_search_service
from app.database import engine
from app.main import app
from app.models import Chunk, Document, User
from app.services.embeddings import EMBEDDING_DIMENSION


client = TestClient(app)

USER_PASSWORD = "SemanticTestPassword123!"


@pytest.fixture(autouse=True)
def clear_database():
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


def create_vector(
    first_value: float,
    second_value: float = 0.0,
) -> list[float]:
    vector = [0.0] * EMBEDDING_DIMENSION
    vector[0] = first_value
    vector[1] = second_value
    return vector


def create_authenticated_user() -> tuple[dict[str, str], int]:
    email = f"semantic-auth-{uuid4()}@example.com"

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

    headers = {
        "Authorization": (
            f"Bearer {login_response.json()['access_token']}"
        )
    }

    me_response = client.get(
        "/auth/me",
        headers=headers,
    )

    assert me_response.status_code == 200

    user_id = int(me_response.json()["id"])

    return headers, user_id


def create_semantic_search_data(owner_id: int) -> None:
    with Session(engine) as session:
        document = Document(
            title="Semantic Search Validation",
            content="Document used to validate semantic search.",
            owner_id=owner_id,
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
    auth_headers, owner_id = create_authenticated_user()
    query_embedding = create_vector(1.0)

    monkeypatch.setattr(
        semantic_search_service,
        "generate_embedding",
        lambda query: query_embedding,
    )

    create_semantic_search_data(owner_id)

    response = client.get(
        "/search/semantic",
        headers=auth_headers,
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
    auth_headers, owner_id = create_authenticated_user()
    query_embedding = create_vector(1.0)

    monkeypatch.setattr(
        semantic_search_service,
        "generate_embedding",
        lambda query: query_embedding,
    )

    create_semantic_search_data(owner_id)

    response = client.get(
        "/search/semantic",
        headers=auth_headers,
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
    auth_headers, _ = create_authenticated_user()
    response = client.get(
        "/search/semantic",
        headers=auth_headers,
        params={"q": "   "},
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Search query cannot be empty."
    )


@pytest.mark.parametrize("top_k", [0, 21])
def test_semantic_search_validates_top_k(top_k):
    auth_headers, _ = create_authenticated_user()
    response = client.get(
        "/search/semantic",
        headers=auth_headers,
        params={
            "q": "lunar exploration",
            "top_k": top_k,
        },
    )

    assert response.status_code == 422
    
def test_semantic_search_filters_results_by_max_distance(
    monkeypatch,
):
    auth_headers, owner_id = create_authenticated_user()
    query_embedding = create_vector(1.0)

    monkeypatch.setattr(
        semantic_search_service,
        "generate_embedding",
        lambda query: query_embedding,
    )

    create_semantic_search_data(owner_id)

    response = client.get(
        "/search/semantic",
        headers=auth_headers,
        params={
            "q": "lunar exploration",
            "top_k": 10,
            "max_distance": 0.25,
        },
    )

    assert response.status_code == 200

    results = response.json()

    assert len(results) == 2
    assert [result["content"] for result in results] == [
        "Exact semantic match.",
        "Related semantic match.",
    ]

    assert all(
        result["distance"] <= 0.25
        for result in results
    )


def test_semantic_search_returns_empty_list_when_all_results_exceed_threshold(
    monkeypatch,
):
    auth_headers, owner_id = create_authenticated_user()
    query_embedding = create_vector(-1.0)

    monkeypatch.setattr(
        semantic_search_service,
        "generate_embedding",
        lambda query: query_embedding,
    )

    create_semantic_search_data(owner_id)

    response = client.get(
        "/search/semantic",
        headers=auth_headers,
        params={
            "q": "completely unrelated query",
            "top_k": 10,
            "max_distance": 0.50,
        },
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(
    "max_distance",
    [-0.01, 2.01],
)
def test_semantic_search_validates_max_distance(
    max_distance,
):
    auth_headers, _ = create_authenticated_user()
    response = client.get(
        "/search/semantic",
        headers=auth_headers,
        params={
            "q": "lunar exploration",
            "max_distance": max_distance,
        },
    )

    assert response.status_code == 422



def create_owned_semantic_chunk(
    session: Session,
    *,
    email: str,
    title: str,
    content: str,
    embedding: list[float],
) -> tuple[User, Document, Chunk]:
    owner = User(
        email=email,
        password_hash="test-only-hash",
    )
    session.add(owner)
    session.flush()

    assert owner.id is not None

    document = Document(
        title=title,
        content=content,
        owner_id=owner.id,
    )
    session.add(document)
    session.flush()

    assert document.id is not None

    chunk = Chunk(
        document_id=document.id,
        content=content,
        chunk_index=0,
        char_count=len(content),
        embedding=embedding,
    )
    session.add(chunk)
    session.commit()

    return owner, document, chunk


def test_semantic_search_requires_authentication(
    monkeypatch,
):
    monkeypatch.setattr(
        search_route,
        "search_chunks_semantically",
        lambda **kwargs: [],
    )

    response = client.get(
        "/search/semantic",
        params={"q": "authentication check"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Could not validate credentials."
    }


def test_semantic_search_applies_ownership_before_ranking(
    monkeypatch,
):
    query_embedding = create_vector(1.0)

    monkeypatch.setattr(
        semantic_search_service,
        "generate_embedding",
        lambda query: query_embedding,
    )

    with Session(engine) as session:
        _, other_document, _ = create_owned_semantic_chunk(
            session,
            email=f"semantic-other-{uuid4()}@example.com",
            title="Other owner",
            content="Exact match from another owner.",
            embedding=create_vector(1.0),
        )

        owner, own_document, _ = create_owned_semantic_chunk(
            session,
            email=f"semantic-owner-{uuid4()}@example.com",
            title="Own document",
            content="Allowed semantic result.",
            embedding=create_vector(0.8, 0.6),
        )

        assert owner.id is not None

        results = semantic_search_service.search_chunks_semantically(
            session=session,
            query="controlled query",
            top_k=1,
            owner_id=owner.id,
        )

        assert len(results) == 1

        _, returned_document, _ = results[0]

        assert returned_document.id == own_document.id
        assert returned_document.id != other_document.id
