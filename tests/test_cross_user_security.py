from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlmodel import Session, delete, select

import app.routes.rag as rag_route
import app.services.semantic_search as semantic_search_service
from app.config import settings
from app.database import engine
from app.main import app
from app.models import Chunk, Document, User
from app.services.embeddings import EMBEDDING_DIMENSION


client = TestClient(app)

USER_PASSWORD = "uma senha longa e segura"
TEST_JWT_SECRET = (
    "test-only-secret-key-for-cross-user-security-tests"
)


@pytest.fixture(autouse=True)
def configure_test_jwt(monkeypatch):
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
    first: float,
    second: float = 0.0,
) -> list[float]:
    vector = [0.0] * EMBEDDING_DIMENSION
    vector[0] = first
    vector[1] = second
    return vector


def get_auth_headers_for_user(
    email: str,
) -> dict[str, str]:
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

    return {
        "Authorization": (
            f"Bearer {login_response.json()['access_token']}"
        )
    }


def create_document(
    headers: dict[str, str],
    *,
    title: str,
    content: str,
) -> int:
    response = client.post(
        "/documents",
        headers=headers,
        json={
            "title": title,
            "content": content,
        },
    )

    assert response.status_code == 201

    return int(response.json()["id"])


def set_document_embedding(
    document_id: int,
    embedding: list[float],
) -> None:
    with Session(engine) as session:
        chunk = session.exec(
            select(Chunk).where(
                Chunk.document_id == document_id
            )
        ).first()

        assert chunk is not None

        chunk.embedding = embedding
        session.add(chunk)
        session.commit()


def test_semantic_route_isolates_users_before_ranking(
    monkeypatch,
):
    first_headers = get_auth_headers_for_user(
        "semantic-first@example.com"
    )
    second_headers = get_auth_headers_for_user(
        "semantic-second@example.com"
    )

    first_document_id = create_document(
        first_headers,
        title="Allowed semantic document",
        content="Allowed semantic content.",
    )
    second_document_id = create_document(
        second_headers,
        title="Forbidden semantic document",
        content="Perfect semantic match from another user.",
    )

    set_document_embedding(
        first_document_id,
        create_vector(0.8, 0.6),
    )
    set_document_embedding(
        second_document_id,
        create_vector(1.0),
    )

    monkeypatch.setattr(
        semantic_search_service,
        "generate_embedding",
        lambda query: create_vector(1.0),
    )

    response = client.get(
        "/search/semantic",
        headers=first_headers,
        params={
            "q": "controlled semantic query",
            "top_k": 1,
        },
    )

    assert response.status_code == 200

    results = response.json()

    assert len(results) == 1
    assert int(results[0]["document_id"]) == first_document_id
    assert int(results[0]["document_id"]) != second_document_id


def test_hybrid_route_isolates_users_before_rank_fusion(
    monkeypatch,
):
    first_headers = get_auth_headers_for_user(
        "hybrid-first@example.com"
    )
    second_headers = get_auth_headers_for_user(
        "hybrid-second@example.com"
    )

    first_document_id = create_document(
        first_headers,
        title="Allowed hybrid document",
        content="shared-keyword allowed content.",
    )
    second_document_id = create_document(
        second_headers,
        title="Forbidden hybrid document",
        content="shared-keyword forbidden perfect content.",
    )

    set_document_embedding(
        first_document_id,
        create_vector(0.8, 0.6),
    )
    set_document_embedding(
        second_document_id,
        create_vector(1.0),
    )

    monkeypatch.setattr(
        semantic_search_service,
        "generate_embedding",
        lambda query: create_vector(1.0),
    )

    response = client.get(
        "/search/hybrid",
        headers=first_headers,
        params={
            "q": "shared-keyword",
            "top_k": 1,
        },
    )

    assert response.status_code == 200

    results = response.json()

    assert len(results) == 1
    assert int(results[0]["document_id"]) == first_document_id
    assert int(results[0]["document_id"]) != second_document_id


def test_rag_answer_keeps_other_user_content_out_of_context_and_sources(
    monkeypatch,
):
    first_headers = get_auth_headers_for_user(
        "rag-first@example.com"
    )
    second_headers = get_auth_headers_for_user(
        "rag-second@example.com"
    )

    first_document_id = create_document(
        first_headers,
        title="Allowed RAG document",
        content="shared-keyword allowed RAG evidence.",
    )
    second_document_id = create_document(
        second_headers,
        title="Forbidden RAG document",
        content="shared-keyword forbidden RAG evidence.",
    )

    set_document_embedding(
        first_document_id,
        create_vector(0.8, 0.6),
    )
    set_document_embedding(
        second_document_id,
        create_vector(1.0),
    )

    monkeypatch.setattr(
        semantic_search_service,
        "generate_embedding",
        lambda query: create_vector(1.0),
    )

    captured: dict[str, object] = {}

    fake_evaluator = SimpleNamespace()

    def fake_get_semantic_answerability_evaluator():
        return fake_evaluator

    def fake_evaluate_semantic_answerability(
        evaluator,
        question,
        context,
    ):
        captured["evaluator"] = evaluator
        captured["question"] = question
        captured["context"] = context

        return SimpleNamespace(
            should_abstain=True,
            can_generate=False,
            reason="semantic_evaluation_failed",
        )

    monkeypatch.setattr(
        rag_route,
        "get_semantic_answerability_evaluator",
        fake_get_semantic_answerability_evaluator,
    )
    monkeypatch.setattr(
        rag_route,
        "evaluate_semantic_answerability",
        fake_evaluate_semantic_answerability,
    )

    response = client.post(
        "/rag/answer",
        headers=first_headers,
        json={
            "question": "shared-keyword",
        },
    )

    assert response.status_code == 200

    assert captured["evaluator"] is fake_evaluator
    assert captured["question"] == "shared-keyword"

    context = str(captured["context"])

    assert "allowed RAG evidence" in context
    assert "forbidden RAG evidence" not in context
    assert "Forbidden RAG document" not in context

    body = response.json()

    assert body["answer"] is None
    assert body["abstained"] is True

    assert len(body["sources"]) == 1

    source = body["sources"][0]

    assert int(source["document_id"]) == first_document_id
    assert int(source["document_id"]) != second_document_id
    assert source["document_title"] == "Allowed RAG document"
    assert source["content"] == (
        "shared-keyword allowed RAG evidence."
    )
