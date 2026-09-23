from collections.abc import Sequence
from dataclasses import dataclass

from evaluation.layered import (
    EvaluationLayer,
    LayerStatus,
    LayeredEvaluationResult,
)
from evaluation.metrics import calculate_rate


@dataclass(frozen=True)
class LayerStatusSummary:
    total_cases: int
    evaluated_cases: int
    passed_cases: int
    failed_cases: int
    blocked_cases: int
    not_evaluated_cases: int
    pass_rate: float


@dataclass(frozen=True)
class LayeredEvaluationSummary:
    total_cases: int
    retrieval: LayerStatusSummary
    context: LayerStatusSummary
    answerability: LayerStatusSummary
    generation: LayerStatusSummary
    first_failure_counts: dict[
        EvaluationLayer,
        int,
    ]
    cases_with_failure: int
    no_failure_observed_cases: int
    observed_failure_rate: float


def summarize_layer_statuses(
    statuses: Sequence[LayerStatus],
) -> LayerStatusSummary:
    passed_cases = sum(
        status == LayerStatus.PASS
        for status in statuses
    )

    failed_cases = sum(
        status == LayerStatus.FAIL
        for status in statuses
    )

    blocked_cases = sum(
        status == LayerStatus.BLOCKED
        for status in statuses
    )

    not_evaluated_cases = sum(
        status == LayerStatus.NOT_EVALUATED
        for status in statuses
    )

    evaluated_cases = (
        passed_cases
        + failed_cases
    )

    return LayerStatusSummary(
        total_cases=len(statuses),
        evaluated_cases=evaluated_cases,
        passed_cases=passed_cases,
        failed_cases=failed_cases,
        blocked_cases=blocked_cases,
        not_evaluated_cases=not_evaluated_cases,
        pass_rate=calculate_rate(
            passed_cases,
            evaluated_cases,
        ),
    )


def summarize_layered_results(
    results: Sequence[LayeredEvaluationResult],
) -> LayeredEvaluationSummary:
    total_cases = len(results)

    first_failure_counts = {
        layer: sum(
            result.first_failure == layer
            for result in results
        )
        for layer in EvaluationLayer
    }

    cases_with_failure = sum(
        result.first_failure is not None
        for result in results
    )

    return LayeredEvaluationSummary(
        total_cases=total_cases,
        retrieval=summarize_layer_statuses(
            [
                result.retrieval
                for result in results
            ]
        ),
        context=summarize_layer_statuses(
            [
                result.context
                for result in results
            ]
        ),
        answerability=summarize_layer_statuses(
            [
                result.answerability
                for result in results
            ]
        ),
        generation=summarize_layer_statuses(
            [
                result.generation
                for result in results
            ]
        ),
        first_failure_counts=(
            first_failure_counts
        ),
        cases_with_failure=cases_with_failure,
        no_failure_observed_cases=(
            total_cases - cases_with_failure
        ),
        observed_failure_rate=calculate_rate(
            cases_with_failure,
            total_cases,
        ),
    )