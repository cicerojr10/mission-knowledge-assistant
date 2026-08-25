from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlmodel import Session, delete

import app.routes.rag as rag_route
from app.config import settings
from app.database import engine
from app.main import app
from app.models import Chunk, Document, User


client = TestClient(app)

USER_PASSWORD = "uma senha longa e segura"
TEST_JWT_SECRET = (
    "test-only-secret-key-for-rag-route-tests"
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
def clear_rag_data():
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


def get_auth_headers() -> dict[str, str]:
    email = f"rag-{uuid4()}@example.com"

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


def test_rag_answer_requires_authentication():
    response = client.post(
        "/rag/answer",
        json={
            "question": "What does the document say?",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Could not validate credentials."
    }
    assert response.headers["www-authenticate"] == "Bearer"


def test_rag_answer_abstains_when_no_authorized_context():
    response = client.post(
        "/rag/answer",
        headers=get_auth_headers(),
        json={
            "question": "What does the document say?",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": None,
        "abstained": True,
        "sources": [],
    }

def test_rag_answer_uses_context_evidence_as_sources(
    monkeypatch,
):
    headers = get_auth_headers()

    me_response = client.get(
        "/auth/me",
        headers=headers,
    )
    assert me_response.status_code == 200

    expected_owner_id = int(
        me_response.json()["id"]
    )

    first_result = SimpleNamespace(
        chunk=SimpleNamespace(
            id=501,
            content="First retrieved candidate.",
            chunk_index=0,
        ),
        document=SimpleNamespace(
            id=601,
            title="First document",
        ),
    )

    second_result = SimpleNamespace(
        chunk=SimpleNamespace(
            id=502,
            content="Selected context evidence.",
            chunk_index=1,
        ),
        document=SimpleNamespace(
            id=602,
            title="Selected document",
        ),
    )

    captured: dict[str, object] = {}

    def fake_search_chunks_hybrid(**kwargs):
        captured["owner_id"] = kwargs["owner_id"]
        captured["query"] = kwargs["query"]

        return [
            first_result,
            second_result,
        ]

    def fake_build_rag_context(results):
        captured["context_results"] = results

        return SimpleNamespace(
            text="Selected context.",
            evidence=(second_result,),
        )

    monkeypatch.setattr(
        rag_route,
        "search_chunks_hybrid",
        fake_search_chunks_hybrid,
    )
    monkeypatch.setattr(
        rag_route,
        "build_rag_context",
        fake_build_rag_context,
        raising=False,
    )

    response = client.post(
        "/rag/answer",
        headers=headers,
        json={
            "question": "What is authorized?",
        },
    )

    assert response.status_code == 200

    assert captured["owner_id"] == expected_owner_id
    assert captured["query"] == "What is authorized?"
    assert captured["context_results"] == [
        first_result,
        second_result,
    ]

    assert response.json()["answer"] is None
    assert response.json()["sources"] == [
        {
            "chunk_id": "502",
            "document_id": "602",
            "document_title": "Selected document",
            "content": "Selected context evidence.",
            "chunk_index": 1,
        }
    ]

def test_rag_answer_generates_when_answerability_allows(
    monkeypatch,
):
    headers = get_auth_headers()

    selected_result = SimpleNamespace(
        chunk=SimpleNamespace(
            id=701,
            content="Selected authorized evidence.",
            chunk_index=0,
        ),
        document=SimpleNamespace(
            id=801,
            title="Selected document",
        ),
    )

    fake_generator = SimpleNamespace()

    def fake_search_chunks_hybrid(**kwargs):
        return [selected_result]

    def fake_build_rag_context(results):
        return SimpleNamespace(
            text="Formatted authorized context.",
            evidence=(selected_result,),
        )

    def fake_assess_answerability(context):
        return SimpleNamespace(
            should_abstain=False,
            can_generate=True,
            reason="semantic_evaluation_passed",
        )

    def fake_get_generator():
        return fake_generator

    def fake_generate_if_allowed(
        decision,
        generator,
        question,
        context,
    ):
        assert decision.can_generate is True
        assert generator is fake_generator
        assert question == "What happened?"
        assert context == "Formatted authorized context."

        return SimpleNamespace(
            text="Generated answer.",
        )

    monkeypatch.setattr(
        rag_route,
        "search_chunks_hybrid",
        fake_search_chunks_hybrid,
    )
    monkeypatch.setattr(
        rag_route,
        "build_rag_context",
        fake_build_rag_context,
    )
    monkeypatch.setattr(
        rag_route,
        "assess_answerability",
        fake_assess_answerability,
        raising=False,
    )
    monkeypatch.setattr(
        rag_route,
        "get_generator",
        fake_get_generator,
        raising=False,
    )
    monkeypatch.setattr(
        rag_route,
        "generate_if_allowed",
        fake_generate_if_allowed,
        raising=False,
    )

    response = client.post(
        "/rag/answer",
        headers=headers,
        json={
            "question": "What happened?",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Generated answer.",
        "abstained": False,
        "sources": [
            {
                "chunk_id": "701",
                "document_id": "801",
                "document_title": "Selected document",
                "content": "Selected authorized evidence.",
                "chunk_index": 0,
            }
        ],
    }
