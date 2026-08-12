from dataclasses import dataclass

from sqlmodel import Session, select

from app.models import Chunk, Document
from app.services.rank_fusion import reciprocal_rank_fusion
from app.services.semantic_search import (
    search_chunks_semantically,
)


@dataclass(frozen=True)
class HybridSearchResult:
    chunk: Chunk
    document: Document
    rrf_score: float
    textual_rank: int | None
    semantic_rank: int | None
    semantic_distance: float | None


def get_persisted_chunk_id(chunk: Chunk) -> int:
    """
    Retorna o ID de um chunk persistido.

    A busca híbrida trabalha somente com registros existentes
    no banco, portanto o ID não pode ser nulo.
    """
    if chunk.id is None:
        raise RuntimeError(
            "Persisted chunk does not have an ID."
        )

    return chunk.id


def search_chunks_hybrid(
    session: Session,
    query: str,
    top_k: int,
    owner_id: int,
    max_distance: float | None = None,
    rrf_k: int = 60,
) -> list[HybridSearchResult]:
    """
    Combina busca textual e semântica usando RRF.

    top_k controla:

    - a quantidade de candidatos de cada método;
    - a quantidade máxima no ranking híbrido final.
    """
    if top_k < 1:
        raise ValueError(
            "top_k must be at least 1."
        )

    textual_statement = (
        select(Chunk, Document)
        .where(Chunk.document_id == Document.id)
        .where(Document.owner_id == owner_id)
        .where(Chunk.content.ilike(f"%{query}%"))
        .order_by(
            Document.id,
            Chunk.chunk_index,
        )
        .limit(top_k)
    )

    textual_results = list(
        session.exec(textual_statement).all()
    )

    semantic_results = list(
        search_chunks_semantically(
            session=session,
            query=query,
            top_k=top_k,
            owner_id=owner_id,
            max_distance=max_distance,
        )
    )

    textual_item_ids: list[int] = []
    semantic_item_ids: list[int] = []

    rows_by_chunk_id: dict[
        int,
        tuple[Chunk, Document],
    ] = {}

    semantic_distances: dict[int, float] = {}

    for chunk, document in textual_results:
        chunk_id = get_persisted_chunk_id(chunk)

        textual_item_ids.append(chunk_id)

        rows_by_chunk_id.setdefault(
            chunk_id,
            (chunk, document),
        )

    for chunk, document, distance in semantic_results:
        chunk_id = get_persisted_chunk_id(chunk)

        semantic_item_ids.append(chunk_id)

        rows_by_chunk_id.setdefault(
            chunk_id,
            (chunk, document),
        )

        semantic_distances[chunk_id] = float(
            distance
        )

    fused_ranking = reciprocal_rank_fusion(
        textual_item_ids=textual_item_ids,
        semantic_item_ids=semantic_item_ids,
        rrf_k=rrf_k,
    )

    hybrid_results: list[HybridSearchResult] = []

    for fused_result in fused_ranking[:top_k]:
        chunk, document = rows_by_chunk_id[
            fused_result.item_id
        ]

        hybrid_results.append(
            HybridSearchResult(
                chunk=chunk,
                document=document,
                rrf_score=fused_result.rrf_score,
                textual_rank=(
                    fused_result.textual_rank
                ),
                semantic_rank=(
                    fused_result.semantic_rank
                ),
                semantic_distance=(
                    semantic_distances.get(
                        fused_result.item_id
                    )
                ),
            )
        )

    return hybrid_results
