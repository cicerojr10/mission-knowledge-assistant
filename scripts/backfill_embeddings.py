from collections.abc import Callable, Sequence

from sqlmodel import Session, select

from app.database import engine
from app.models import Chunk
from app.services.embeddings import (
    EMBEDDING_DIMENSION,
    generate_embeddings,
)


EmbeddingGenerator = Callable[[Sequence[str]], list[list[float]]]


def backfill_embeddings(
    session: Session,
    embedding_generator: EmbeddingGenerator = generate_embeddings,
) -> int:
    """
    Gera e persiste embeddings somente para chunks ainda não processados.

    Retorna a quantidade de chunks atualizados.
    """
    statement = (
        select(Chunk)
        .where(Chunk.embedding.is_(None))
        .order_by(Chunk.id)
    )

    chunks = list(session.exec(statement).all())

    if not chunks:
        return 0

    texts = [chunk.content for chunk in chunks]
    vectors = embedding_generator(texts)

    if len(vectors) != len(chunks):
        raise ValueError(
            "Embedding count does not match chunk count: "
            f"{len(vectors)} embeddings for {len(chunks)} chunks."
        )

    try:
        for chunk, vector in zip(chunks, vectors, strict=True):
            if len(vector) != EMBEDDING_DIMENSION:
                raise ValueError(
                    f"Chunk {chunk.id} received an embedding with "
                    f"{len(vector)} dimensions; expected "
                    f"{EMBEDDING_DIMENSION}."
                )

            chunk.embedding = vector
            session.add(chunk)

        session.commit()

    except Exception:
        session.rollback()
        raise

    return len(chunks)


def main() -> None:
    with Session(engine) as session:
        processed_count = backfill_embeddings(session)

    print(f"Chunks processed: {processed_count}")


if __name__ == "__main__":
    main()