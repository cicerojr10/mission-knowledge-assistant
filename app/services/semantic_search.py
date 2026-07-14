from collections.abc import Sequence
from typing import TypeAlias

from sqlmodel import Session, select

from app.models import Chunk, Document
from app.services.embeddings import generate_embedding


SemanticSearchRow: TypeAlias = tuple[Chunk, Document, float]


def search_chunks_semantically(
    session: Session,
    query: str,
    top_k: int,
) -> Sequence[SemanticSearchRow]:
    """
    Retorna os chunks com menor distância de cosseno
    em relação ao embedding da consulta.
    """
    query_embedding = generate_embedding(query)

    distance = Chunk.embedding.cosine_distance(
        query_embedding
    ).label("distance")

    statement = (
        select(Chunk, Document, distance)
        .where(Chunk.document_id == Document.id)
        .where(Chunk.embedding.is_not(None))
        .order_by(distance)
        .limit(top_k)
    )

    return session.exec(statement).all()