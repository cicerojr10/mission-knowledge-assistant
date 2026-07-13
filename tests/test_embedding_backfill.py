from collections.abc import Sequence

import numpy as np
import pytest
from sqlmodel import Session, delete, select

from app.database import engine
from app.models import Chunk, Document
from app.services.embeddings import EMBEDDING_DIMENSION
from scripts.backfill_embeddings import backfill_embeddings


def clean_database() -> None:
    with Session(engine) as session:
        session.exec(delete(Chunk))
        session.exec(delete(Document))
        session.commit()


def setup_function() -> None:
    clean_database()


def teardown_function() -> None:
    clean_database()


def create_chunks(
    session: Session,
    *,
    embeddings: list[list[float] | None],
) -> list[Chunk]:
    document = Document(
        title="Embedding backfill test",
        content="Document used to test embedding persistence.",
    )
    session.add(document)
    session.flush()

    assert document.id is not None

    chunks: list[Chunk] = []

    for index, embedding in enumerate(embeddings):
        content = f"Test chunk number {index}."

        chunk = Chunk(
            document_id=document.id,
            content=content,
            chunk_index=index,
            char_count=len(content),
            embedding=embedding,
        )
        session.add(chunk)
        chunks.append(chunk)

    session.commit()

    return chunks


def test_backfill_processes_only_chunks_without_embedding() -> None:
    existing_embedding = [0.25] * EMBEDDING_DIMENSION
    generated_embedding = [0.50] * EMBEDDING_DIMENSION
    received_texts: list[str] = []

    def fake_generator(texts: Sequence[str]) -> list[list[float]]:
        received_texts.extend(texts)
        return [generated_embedding.copy() for _ in texts]

    with Session(engine) as session:
        create_chunks(
            session,
            embeddings=[None, existing_embedding],
        )

        processed_count = backfill_embeddings(
            session,
            embedding_generator=fake_generator,
        )

        session.expire_all()

        chunks = list(
            session.exec(
                select(Chunk).order_by(Chunk.chunk_index)
            ).all()
        )

    assert processed_count == 1
    assert received_texts == ["Test chunk number 0."]
    assert np.allclose(chunks[0].embedding, generated_embedding)
    assert np.allclose(chunks[1].embedding, existing_embedding)


def test_backfill_is_idempotent() -> None:
    generated_embedding = [0.75] * EMBEDDING_DIMENSION

    def fake_generator(texts: Sequence[str]) -> list[list[float]]:
        return [generated_embedding.copy() for _ in texts]

    def unexpected_generator(
        texts: Sequence[str],
    ) -> list[list[float]]:
        raise AssertionError(
            f"Generator should not be called for {list(texts)}."
        )

    with Session(engine) as session:
        create_chunks(session, embeddings=[None])

        first_count = backfill_embeddings(
            session,
            embedding_generator=fake_generator,
        )
        second_count = backfill_embeddings(
            session,
            embedding_generator=unexpected_generator,
        )

    assert first_count == 1
    assert second_count == 0


def test_backfill_rolls_back_invalid_embedding_dimensions() -> None:
    valid_embedding = [0.10] * EMBEDDING_DIMENSION
    invalid_embedding = [0.20] * (EMBEDDING_DIMENSION - 1)

    def invalid_generator(
        texts: Sequence[str],
    ) -> list[list[float]]:
        assert len(texts) == 2
        return [valid_embedding, invalid_embedding]

    with Session(engine) as session:
        create_chunks(session, embeddings=[None, None])

        with pytest.raises(ValueError, match="383 dimensions"):
            backfill_embeddings(
                session,
                embedding_generator=invalid_generator,
            )

        session.expire_all()

        chunks = list(
            session.exec(
                select(Chunk).order_by(Chunk.chunk_index)
            ).all()
        )

    assert all(chunk.embedding is None for chunk in chunks)