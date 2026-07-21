import pytest

from app.services.rank_fusion import (
    get_first_positions,
    reciprocal_rank_fusion,
)


def test_get_first_positions_keeps_first_occurrence():
    positions = get_first_positions(
        [10, 10, 20]
    )

    assert positions == {
        10: 1,
        20: 3,
    }


def test_reciprocal_rank_fusion_promotes_shared_item():
    results = reciprocal_rank_fusion(
        textual_item_ids=[1, 4],
        semantic_item_ids=[1, 2, 3],
    )

    assert [
        result.item_id
        for result in results
    ] == [1, 2, 4, 3]

    first_result = results[0]

    assert first_result.item_id == 1
    assert first_result.textual_rank == 1
    assert first_result.semantic_rank == 1
    assert first_result.rrf_score == pytest.approx(
        (1 / 61) + (1 / 61)
    )


def test_reciprocal_rank_fusion_returns_empty_list():
    results = reciprocal_rank_fusion(
        textual_item_ids=[],
        semantic_item_ids=[],
    )

    assert results == []


def test_reciprocal_rank_fusion_rejects_invalid_rrf_k():
    with pytest.raises(
        ValueError,
        match="rrf_k must be at least 1",
    ):
        reciprocal_rank_fusion(
            textual_item_ids=[1],
            semantic_item_ids=[1],
            rrf_k=0,
        )


def test_reciprocal_rank_fusion_uses_deterministic_tie_break():
    results = reciprocal_rank_fusion(
        textual_item_ids=[20],
        semantic_item_ids=[10],
    )

    assert [
        result.item_id
        for result in results
    ] == [10, 20]

    assert results[0].semantic_rank == 1
    assert results[1].textual_rank == 1