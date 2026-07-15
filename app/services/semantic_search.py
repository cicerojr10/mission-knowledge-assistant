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
    max_distance: float | None = None,
) -> Sequence[SemanticSearchRow]:
    """
    Retorna os chunks com menor distância de cosseno
    em relação ao embedding da consulta.

    Quando max_distance é informado, exclui resultados cuja
    distância ultrapasse o limite de relevância definido.
    """
    query_embedding = generate_embedding(query)

    distance_expression = Chunk.embedding.cosine_distance(
        query_embedding
    )

    distance = distance_expression.label("distance")

    statement = (
        select(Chunk, Document, distance)
        .where(Chunk.document_id == Document.id)
        .where(Chunk.embedding.is_not(None))
    )

    if max_distance is not None:
        statement = statement.where(
            distance_expression <= max_distance
        )

    statement = (
        statement
        .order_by(distance_expression)
        .limit(top_k)
    )

    return session.exec(statement).all()