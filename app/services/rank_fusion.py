from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class FusedRank:
    item_id: int
    rrf_score: float
    textual_rank: int | None
    semantic_rank: int | None


def get_first_positions(
    ranking: Sequence[int],
) -> dict[int, int]:
    """
    Registra somente a primeira posição de cada item.

    Caso um item apareça repetido no mesmo ranking,
    ele recebe apenas uma contribuição.
    """
    positions: dict[int, int] = {}

    for position, item_id in enumerate(
        ranking,
        start=1,
    ):
        positions.setdefault(item_id, position)

    return positions


def reciprocal_rank_fusion(
    textual_item_ids: Sequence[int],
    semantic_item_ids: Sequence[int],
    *,
    rrf_k: int = 60,
) -> list[FusedRank]:
    """
    Combina dois rankings usando Reciprocal Rank Fusion.

    Cada item recebe:

        1 / (rrf_k + posição)

    para cada ranking em que aparece.
    """
    if rrf_k < 1:
        raise ValueError(
            "rrf_k must be at least 1."
        )

    textual_positions = get_first_positions(
        textual_item_ids
    )

    semantic_positions = get_first_positions(
        semantic_item_ids
    )

    all_item_ids = (
        set(textual_positions)
        | set(semantic_positions)
    )

    fused_results: list[FusedRank] = []

    for item_id in all_item_ids:
        textual_rank = textual_positions.get(
            item_id
        )

        semantic_rank = semantic_positions.get(
            item_id
        )

        rrf_score = 0.0

        if textual_rank is not None:
            rrf_score += 1 / (
                rrf_k + textual_rank
            )

        if semantic_rank is not None:
            rrf_score += 1 / (
                rrf_k + semantic_rank
            )

        fused_results.append(
            FusedRank(
                item_id=item_id,
                rrf_score=rrf_score,
                textual_rank=textual_rank,
                semantic_rank=semantic_rank,
            )
        )

    return sorted(
        fused_results,
        key=lambda result: (
            -result.rrf_score,
            (
                result.semantic_rank
                if result.semantic_rank is not None
                else float("inf")
            ),
            (
                result.textual_rank
                if result.textual_rank is not None
                else float("inf")
            ),
            result.item_id,
        ),
    )