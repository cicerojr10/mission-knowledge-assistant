from types import SimpleNamespace

import pytest
from sqlmodel import Session, select

import evaluation.retrieval_executor as retrieval_executor
from app.database import engine
from app.models import Document, User
from app.services.embeddings import EMBEDDING_DIMENSION
from evaluation.models import (
    EvaluationCase,
    EvaluationCategory,
    EvaluationDocument,
)
from evaluation.retrieval_executor import (
    SeededEvaluationCorpus,
    cleanup_evaluation_corpus,
    execute_retrieval_case,
    seed_evaluation_corpus,
)


def create_embedding() -> list[float]:
    return [0.0] * EMBEDDING_DIMENSION


def test_seed_and_cleanup_evaluation_corpus(
    monkeypatch,
):
    monkeypatch.setattr(
        retrieval_executor,
        "hash_password",
        lambda password: "test-only-hash",
    )

    monkeypatch.setattr(
        retrieval_executor,
        "generate_embeddings",
        lambda texts: [
            create_embedding()
            for _ in texts
        ],
    )

    documents = [
        EvaluationDocument(
            key="primary-document",
            owner_key="primary",
            title="Primary",
            content="Primary evaluation content.",
        ),
        EvaluationDocument(
            key="secondary-document",
            owner_key="secondary",
            title="Secondary",
            content="Secondary evaluation content.",
        ),
    ]

    with Session(engine) as session:
        corpus = seed_evaluation_corpus(
            session=session,
            documents=documents,
        )

        try:
            assert set(corpus.owner_ids) == {
                "primary",
                "secondary",
            }

            assert set(
                corpus.document_keys_by_id.values()
            ) == {
                "primary-document",
                "secondary-document",
            }

            persisted_documents = session.exec(
                select(Document).where(
                    Document.id.in_(
                        corpus.document_ids
                    )
                )
            ).all()

            assert len(persisted_documents) == 2

        finally:
            cleanup_evaluation_corpus(
                session=session,
                corpus=corpus,
            )

        remaining_users = session.exec(
            select(User).where(
                User.id.in_(
                    corpus.user_ids
                )
            )
        ).all()

        remaining_documents = session.exec(
            select(Document).where(
                Document.id.in_(
                    corpus.document_ids
                )
            )
        ).all()

        assert remaining_users == []
        assert remaining_documents == []


def test_execute_retrieval_case_uses_owner_and_preserves_ranking(
    monkeypatch,
):
    corpus = SeededEvaluationCorpus(
        owner_ids={
            "primary": 10,
        },
        document_keys_by_id={
            100: "doc-a",
            200: "doc-b",
        },
        document_ids=(
            100,
            200,
        ),
        user_ids=(10,),
    )

    case = EvaluationCase(
        id="case-001",
        category=EvaluationCategory.ANSWERABLE,
        owner_key="primary",
        question="Evaluation question?",
        expected_abstained=False,
        expected_document_keys=("doc-a",),
        forbidden_document_keys=(),
    )

    captured: dict[str, object] = {}

    def fake_search_chunks_hybrid(
        **kwargs,
    ):
        captured.update(kwargs)

        return [
            SimpleNamespace(
                document=SimpleNamespace(id=200)
            ),
            SimpleNamespace(
                document=SimpleNamespace(id=100)
            ),
            SimpleNamespace(
                document=SimpleNamespace(id=200)
            ),
        ]

    monkeypatch.setattr(
        retrieval_executor,
        "search_chunks_hybrid",
        fake_search_chunks_hybrid,
    )

    observation = execute_retrieval_case(
        session=object(),
        case=case,
        corpus=corpus,
        top_k=3,
        max_distance=0.7,
    )

    assert observation.document_keys == (
        "doc-b",
        "doc-a",
    )

    assert captured["query"] == (
        "Evaluation question?"
    )

    assert captured["top_k"] == 3
    assert captured["owner_id"] == 10
    assert captured["max_distance"] == 0.7


def test_execute_retrieval_case_rejects_unknown_owner():
    corpus = SeededEvaluationCorpus(
        owner_ids={
            "primary": 10,
        },
        document_keys_by_id={},
        document_ids=(),
        user_ids=(10,),
    )

    case = EvaluationCase(
        id="case-001",
        category=EvaluationCategory.CROSS_USER,
        owner_key="missing-owner",
        question="Question?",
        expected_abstained=True,
        expected_document_keys=(),
        forbidden_document_keys=(),
    )

    with pytest.raises(
        ValueError,
        match=(
            "Evaluation case references "
            "unknown owner 'missing-owner'."
        ),
    ):
        execute_retrieval_case(
            session=object(),
            case=case,
            corpus=corpus,
        )