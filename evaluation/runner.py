from collections.abc import Callable, Sequence

from evaluation.models import (
    EvaluationCase,
    EvaluationObservation,
    EvaluationResult,
)


EvaluationExecutor = Callable[
    [EvaluationCase],
    EvaluationObservation,
]


def evaluate_case(
    case: EvaluationCase,
    observation: EvaluationObservation,
) -> EvaluationResult:
    observed_document_keys = set(
        observation.document_keys
    )

    expected_documents_found = (
        set(case.expected_document_keys)
        <= observed_document_keys
    )

    forbidden_documents_absent = (
        observed_document_keys.isdisjoint(
            case.forbidden_document_keys
        )
    )

    abstention_matches = (
        observation.abstained
        is case.expected_abstained
    )

    passed = all(
        (
            abstention_matches,
            expected_documents_found,
            forbidden_documents_absent,
        )
    )

    return EvaluationResult(
        case_id=case.id,
        category=case.category,
        passed=passed,
        abstention_matches=abstention_matches,
        expected_documents_found=(
            expected_documents_found
        ),
        forbidden_documents_absent=(
            forbidden_documents_absent
        ),
    )


def run_evaluation(
    cases: Sequence[EvaluationCase],
    executor: EvaluationExecutor,
) -> list[EvaluationResult]:
    return [
        evaluate_case(
            case=case,
            observation=executor(case),
        )
        for case in cases
    ]
