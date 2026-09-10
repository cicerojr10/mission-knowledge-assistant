from collections.abc import Sequence

from evaluation.models import (
    EvaluationCategory,
    EvaluationResult,
    EvaluationSummary,
)


def calculate_rate(
    successful_cases: int,
    total_cases: int,
) -> float:
    if total_cases == 0:
        return 0.0

    return successful_cases / total_cases


def summarize_results(
    results: Sequence[EvaluationResult],
) -> EvaluationSummary:
    total_cases = len(results)

    passed_cases = sum(
        result.passed
        for result in results
    )

    abstention_matches = sum(
        result.abstention_matches
        for result in results
    )

    expected_documents_found = sum(
        result.expected_documents_found
        for result in results
    )

    forbidden_documents_absent = sum(
        result.forbidden_documents_absent
        for result in results
    )

    return EvaluationSummary(
        total_cases=total_cases,
        passed_cases=passed_cases,
        pass_rate=calculate_rate(
            passed_cases,
            total_cases,
        ),
        abstention_match_rate=calculate_rate(
            abstention_matches,
            total_cases,
        ),
        expected_documents_found_rate=calculate_rate(
            expected_documents_found,
            total_cases,
        ),
        forbidden_documents_absent_rate=calculate_rate(
            forbidden_documents_absent,
            total_cases,
        ),
    )


def summarize_results_by_category(
    results: Sequence[EvaluationResult],
) -> dict[
    EvaluationCategory,
    EvaluationSummary,
]:
    summaries: dict[
        EvaluationCategory,
        EvaluationSummary,
    ] = {}

    for category in EvaluationCategory:
        category_results = [
            result
            for result in results
            if result.category == category
        ]

        summaries[category] = summarize_results(
            category_results
        )

    return summaries
