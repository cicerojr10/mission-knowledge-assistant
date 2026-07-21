import pytest
from sqlmodel import Session, delete

import app.services.hybrid_search as hybrid_search_service
from app.database import engine
from app.models import Chunk, Document
from app.services.hybrid_search import (
    get_persisted_chunk_id,
    search_chunks_hybrid,
)


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


def create_document_with_chunk(
    session: Session,
    *,
    title: str,
    content: str,
) -> tuple[Document, Chunk]:
    document = Document(
        title=title,
        content=content,
    )

    session.add(document)
    session.flush()

    if document.id is None:
        raise RuntimeError(
            "Document ID was not generated."
        )

    chunk = Chunk(
        document_id=document.id,
        content=content,
        chunk_index=0,
        char_count=len(content),
        embedding=None,
    )

    session.add(chunk)
    session.commit()

    session.refresh(document)
    session.refresh(chunk)

    return document, chunk


def test_hybrid_search_promotes_result_found_by_both_methods(
    monkeypatch,
):
    with Session(engine) as session:
        artemis_document, artemis_chunk = (
            create_document_with_chunk(
                session,
                title="Artemis Program",
                content=(
                    "The Artemis program will return "
                    "astronauts to the Moon."
                ),
            )
        )

        database_document, database_chunk = (
            create_document_with_chunk(
                session,
                title="PostgreSQL",
                content=(
                    "PostgreSQL is a relational database."
                ),
            )
        )

        def fake_semantic_search(
            session: Session,
            query: str,
            top_k: int,
            max_distance: float | None = None,
        ):
            return [
                (
                    artemis_chunk,
                    artemis_document,
                    0.20,
                ),
                (
                    database_chunk,
                    database_document,
                    0.40,
                ),
            ]

        monkeypatch.setattr(
            hybrid_search_service,
            "search_chunks_semantically",
            fake_semantic_search,
        )

        results = search_chunks_hybrid(
            session=session,
            query="Artemis",
            top_k=2,
            max_distance=0.60,
        )

    assert [
        result.chunk.id
        for result in results
    ] == [
        artemis_chunk.id,
        database_chunk.id,
    ]

    first_result = results[0]

    assert first_result.textual_rank == 1
    assert first_result.semantic_rank == 1
    assert first_result.semantic_distance == pytest.approx(
        0.20
    )

    assert first_result.rrf_score == pytest.approx(
        (1 / 61) + (1 / 61)
    )


def test_hybrid_search_returns_semantic_only_result(
    monkeypatch,
):
    with Session(engine) as session:
        document, chunk = create_document_with_chunk(
            session,
            title="Password Recovery",
            content=(
                "Users can request a password reset link "
                "by email."
            ),
        )

        def fake_semantic_search(
            session: Session,
            query: str,
            top_k: int,
            max_distance: float | None = None,
        ):
            return [
                (
                    chunk,
                    document,
                    0.35,
                )
            ]

        monkeypatch.setattr(
            hybrid_search_service,
            "search_chunks_semantically",
            fake_semantic_search,
        )

        results = search_chunks_hybrid(
            session=session,
            query=(
                "I cannot enter my account."
            ),
            top_k=5,
            max_distance=0.60,
        )

    assert len(results) == 1

    result = results[0]

    assert result.chunk.id == chunk.id
    assert result.textual_rank is None
    assert result.semantic_rank == 1
    assert result.semantic_distance == pytest.approx(
        0.35
    )


def test_hybrid_search_forwards_semantic_parameters(
    monkeypatch,
):
    received_arguments = {}

    def fake_semantic_search(
        session: Session,
        query: str,
        top_k: int,
        max_distance: float | None = None,
    ):
        received_arguments["query"] = query
        received_arguments["top_k"] = top_k
        received_arguments["max_distance"] = (
            max_distance
        )

        return []

    monkeypatch.setattr(
        hybrid_search_service,
        "search_chunks_semantically",
        fake_semantic_search,
    )

    with Session(engine) as session:
        results = search_chunks_hybrid(
            session=session,
            query="controlled query",
            top_k=3,
            max_distance=0.55,
        )

    assert results == []

    assert received_arguments == {
        "query": "controlled query",
        "top_k": 3,
        "max_distance": 0.55,
    }


def test_hybrid_search_rejects_invalid_top_k():
    with Session(engine) as session:
        with pytest.raises(
            ValueError,
            match="top_k must be at least 1",
        ):
            search_chunks_hybrid(
                session=session,
                query="test",
                top_k=0,
            )


def test_get_persisted_chunk_id_rejects_missing_id():
    chunk = Chunk(
        document_id=1,
        content="Not persisted.",
        chunk_index=0,
        char_count=14,
        embedding=None,
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "Persisted chunk does not have an ID"
        ),
    ):
        get_persisted_chunk_id(chunk)