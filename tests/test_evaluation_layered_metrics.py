import pytest

from evaluation.layered import (
    EvaluationLayer,
    LayerStatus,
    LayeredEvaluationResult,
)
from evaluation.layered_metrics import (
    summarize_layer_statuses,
    summarize_layered_results,
)


def test_layer_status_summary_separates_statuses():
    summary = summarize_layer_statuses(
        [
            LayerStatus.PASS,
            LayerStatus.PASS,
            LayerStatus.FAIL,
            LayerStatus.BLOCKED,
            LayerStatus.NOT_EVALUATED,
        ]
    )

    assert summary.total_cases == 5
    assert summary.evaluated_cases == 3
    assert summary.passed_cases == 2
    assert summary.failed_cases == 1
    assert summary.blocked_cases == 1
    assert summary.not_evaluated_cases == 1
    assert summary.pass_rate == pytest.approx(
        2 / 3
    )


def test_layer_status_summary_handles_no_evaluated_cases():
    summary = summarize_layer_statuses(
        [
            LayerStatus.BLOCKED,
            LayerStatus.NOT_EVALUATED,
        ]
    )

    assert summary.total_cases == 2
    assert summary.evaluated_cases == 0
    assert summary.passed_cases == 0
    assert summary.failed_cases == 0
    assert summary.blocked_cases == 1
    assert summary.not_evaluated_cases == 1
    assert summary.pass_rate == 0.0


def test_layered_summary_counts_layers_and_first_failures():
    results = [
        LayeredEvaluationResult(
            retrieval=LayerStatus.PASS,
            context=LayerStatus.PASS,
            answerability=LayerStatus.PASS,
            generation=LayerStatus.NOT_EVALUATED,
            first_failure=None,
        ),
        LayeredEvaluationResult(
            retrieval=LayerStatus.FAIL,
            context=LayerStatus.BLOCKED,
            answerability=LayerStatus.BLOCKED,
            generation=LayerStatus.BLOCKED,
            first_failure=EvaluationLayer.RETRIEVAL,
        ),
        LayeredEvaluationResult(
            retrieval=LayerStatus.PASS,
            context=LayerStatus.FAIL,
            answerability=LayerStatus.BLOCKED,
            generation=LayerStatus.BLOCKED,
            first_failure=EvaluationLayer.CONTEXT,
        ),
        LayeredEvaluationResult(
            retrieval=LayerStatus.NOT_EVALUATED,
            context=LayerStatus.PASS,
            answerability=LayerStatus.NOT_EVALUATED,
            generation=LayerStatus.NOT_EVALUATED,
            first_failure=None,
        ),
    ]

    summary = summarize_layered_results(
        results
    )

    assert summary.total_cases == 4

    assert summary.retrieval.evaluated_cases == 3
    assert summary.retrieval.passed_cases == 2
    assert summary.retrieval.failed_cases == 1
    assert (
        summary.retrieval.not_evaluated_cases
        == 1
    )
    assert summary.retrieval.pass_rate == (
        pytest.approx(2 / 3)
    )

    assert summary.context.evaluated_cases == 3
    assert summary.context.passed_cases == 2
    assert summary.context.failed_cases == 1
    assert summary.context.blocked_cases == 1

    assert (
        summary.answerability.evaluated_cases
        == 1
    )
    assert (
        summary.answerability.passed_cases
        == 1
    )
    assert (
        summary.answerability.blocked_cases
        == 2
    )
    assert (
        summary.answerability.not_evaluated_cases
        == 1
    )
    assert summary.answerability.pass_rate == 1.0

    assert summary.generation.evaluated_cases == 0
    assert summary.generation.blocked_cases == 2
    assert (
        summary.generation.not_evaluated_cases
        == 2
    )
    assert summary.generation.pass_rate == 0.0

    assert summary.first_failure_counts == {
        EvaluationLayer.RETRIEVAL: 1,
        EvaluationLayer.CONTEXT: 1,
        EvaluationLayer.ANSWERABILITY: 0,
        EvaluationLayer.GENERATION: 0,
    }

    assert summary.cases_with_failure == 2
    assert summary.no_failure_observed_cases == 2
    assert summary.observed_failure_rate == 0.5


def test_empty_layered_summary_returns_zero_counts():
    summary = summarize_layered_results([])

    assert summary.total_cases == 0
    assert summary.cases_with_failure == 0
    assert summary.no_failure_observed_cases == 0
    assert summary.observed_failure_rate == 0.0

    assert summary.retrieval.total_cases == 0
    assert summary.retrieval.evaluated_cases == 0
    assert summary.retrieval.pass_rate == 0.0

    assert summary.first_failure_counts == {
        EvaluationLayer.RETRIEVAL: 0,
        EvaluationLayer.CONTEXT: 0,
        EvaluationLayer.ANSWERABILITY: 0,
        EvaluationLayer.GENERATION: 0,
    }