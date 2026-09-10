from collections.abc import Sequence
from dataclasses import dataclass

from evaluation.models import (
    EvaluationCase,
    EvaluationCategory,
)
from evaluation.retrieval_executor import (
    RetrievalObservation,
)


@dataclass(frozen=True)
class RetrievalEvaluationResult:
    case_id: str
    category: EvaluationCategory
    document_keys: tuple[str, ...]
    scored: bool
    passed: bool | None
    expected_documents_found: bool | None
    expected_document_count: int
    retrieved_expected_document_count: int
    expected_document_recall: float | None
    first_expected_rank: int | None
    forbidden_documents_absent: bool | None
    forbidden_document_count: int


@dataclass(frozen=True)
class RetrievalEvaluationSummary:
    total_cases: int
    scored_cases: int
    passed_cases: int
    scored_pass_rate: float
    expected_cases: int
    expected_hit_cases: int
    expected_case_hit_rate: float
    expected_document_recall: float
    forbidden_cases: int
    forbidden_clean_cases: int
    forbidden_document_absence_rate: float


def calculate_rate(
    successful: int,
    total: int,
) -> float:
    if total == 0:
        return 0.0

    return successful / total


def evaluate_retrieval_case(
    case: EvaluationCase,
    observation: RetrievalObservation,
) -> RetrievalEvaluationResult:
    observed_keys = tuple(
        observation.document_keys
    )
    observed_key_set = set(observed_keys)

    expected_keys = set(
        case.expected_document_keys
    )
    forbidden_keys = set(
        case.forbidden_document_keys
    )

    expected_document_count = len(
        expected_keys
    )

    retrieved_expected_document_count = sum(
        key in observed_key_set
        for key in expected_keys
    )

    if expected_keys:
        expected_documents_found = (
            retrieved_expected_document_count
            == expected_document_count
        )

        expected_document_recall = (
            retrieved_expected_document_count
            / expected_document_count
        )

        expected_ranks = [
            observed_keys.index(key) + 1
            for key in expected_keys
            if key in observed_key_set
        ]

        first_expected_rank = (
            min(expected_ranks)
            if expected_ranks
            else None
        )
    else:
        expected_documents_found = None
        expected_document_recall = None
        first_expected_rank = None

    if forbidden_keys:
        forbidden_documents_absent = (
            observed_key_set.isdisjoint(
                forbidden_keys
            )
        )
    else:
        forbidden_documents_absent = None

    scored_checks = [
        check
        for check in (
            expected_documents_found,
            forbidden_documents_absent,
        )
        if check is not None
    ]

    scored = bool(scored_checks)

    passed = (
        all(scored_checks)
        if scored
        else None
    )

    return RetrievalEvaluationResult(
        case_id=case.id,
        category=case.category,
        document_keys=observed_keys,
        scored=scored,
        passed=passed,
        expected_documents_found=(
            expected_documents_found
        ),
        expected_document_count=(
            expected_document_count
        ),
        retrieved_expected_document_count=(
            retrieved_expected_document_count
        ),
        expected_document_recall=(
            expected_document_recall
        ),
        first_expected_rank=first_expected_rank,
        forbidden_documents_absent=(
            forbidden_documents_absent
        ),
        forbidden_document_count=len(
            forbidden_keys
        ),
    )


def summarize_retrieval_results(
    results: Sequence[RetrievalEvaluationResult],
) -> RetrievalEvaluationSummary:
    scored_results = [
        result
        for result in results
        if result.scored
    ]

    expected_results = [
        result
        for result in results
        if result.expected_document_count > 0
    ]

    forbidden_results = [
        result
        for result in results
        if result.forbidden_document_count > 0
    ]

    passed_cases = sum(
        result.passed is True
        for result in scored_results
    )

    expected_hit_cases = sum(
        result.expected_documents_found is True
        for result in expected_results
    )

    total_expected_documents = sum(
        result.expected_document_count
        for result in expected_results
    )

    retrieved_expected_documents = sum(
        result.retrieved_expected_document_count
        for result in expected_results
    )

    forbidden_clean_cases = sum(
        result.forbidden_documents_absent is True
        for result in forbidden_results
    )

    return RetrievalEvaluationSummary(
        total_cases=len(results),
        scored_cases=len(scored_results),
        passed_cases=passed_cases,
        scored_pass_rate=calculate_rate(
            passed_cases,
            len(scored_results),
        ),
        expected_cases=len(expected_results),
        expected_hit_cases=expected_hit_cases,
        expected_case_hit_rate=calculate_rate(
            expected_hit_cases,
            len(expected_results),
        ),
        expected_document_recall=calculate_rate(
            retrieved_expected_documents,
            total_expected_documents,
        ),
        forbidden_cases=len(
            forbidden_results
        ),
        forbidden_clean_cases=(
            forbidden_clean_cases
        ),
        forbidden_document_absence_rate=(
            calculate_rate(
                forbidden_clean_cases,
                len(forbidden_results),
            )
        ),
    )
