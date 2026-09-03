from evaluation.models import (
    EvaluationCase,
    EvaluationCategory,
)
from evaluation.retrieval_executor import (
    RetrievalObservation,
)
from evaluation.retrieval_metrics import (
    evaluate_retrieval_case,
    summarize_retrieval_results,
)


def create_case(
    *,
    case_id: str,
    expected_document_keys: tuple[str, ...] = (),
    forbidden_document_keys: tuple[str, ...] = (),
) -> EvaluationCase:
    return EvaluationCase(
        id=case_id,
        category=EvaluationCategory.ANSWERABLE,
        owner_key="primary",
        question="Evaluation question?",
        expected_abstained=False,
        expected_document_keys=(
            expected_document_keys
        ),
        forbidden_document_keys=(
            forbidden_document_keys
        ),
    )


def test_retrieval_case_tracks_expected_rank():
    case = create_case(
        case_id="case-001",
        expected_document_keys=("doc-a",),
    )

    observation = RetrievalObservation(
        document_keys=(
            "doc-b",
            "doc-a",
        )
    )

    result = evaluate_retrieval_case(
        case=case,
        observation=observation,
    )

    assert result.scored is True
    assert result.passed is True
    assert result.expected_documents_found is True
    assert result.expected_document_recall == 1.0
    assert result.first_expected_rank == 2


def test_retrieval_case_does_not_score_without_expectations():
    case = create_case(
        case_id="case-001",
    )

    observation = RetrievalObservation(
        document_keys=("doc-a",)
    )

    result = evaluate_retrieval_case(
        case=case,
        observation=observation,
    )

    assert result.scored is False
    assert result.passed is None
    assert result.expected_documents_found is None
    assert result.forbidden_documents_absent is None


def test_retrieval_summary_separates_expected_and_forbidden_checks():
    expected_case = create_case(
        case_id="case-001",
        expected_document_keys=("doc-a",),
    )

    missing_case = create_case(
        case_id="case-002",
        expected_document_keys=("doc-b",),
    )

    forbidden_case = create_case(
        case_id="case-003",
        forbidden_document_keys=("doc-secret",),
    )

    informational_case = create_case(
        case_id="case-004",
    )

    results = [
        evaluate_retrieval_case(
            expected_case,
            RetrievalObservation(
                document_keys=("doc-a",)
            ),
        ),
        evaluate_retrieval_case(
            missing_case,
            RetrievalObservation(
                document_keys=("doc-c",)
            ),
        ),
        evaluate_retrieval_case(
            forbidden_case,
            RetrievalObservation(
                document_keys=("doc-a",)
            ),
        ),
        evaluate_retrieval_case(
            informational_case,
            RetrievalObservation(
                document_keys=("doc-c",)
            ),
        ),
    ]

    summary = summarize_retrieval_results(
        results
    )

    assert summary.total_cases == 4
    assert summary.scored_cases == 3
    assert summary.passed_cases == 2
    assert summary.scored_pass_rate == (
        2 / 3
    )

    assert summary.expected_cases == 2
    assert summary.expected_hit_cases == 1
    assert summary.expected_case_hit_rate == 0.5
    assert summary.expected_document_recall == 0.5

    assert summary.forbidden_cases == 1
    assert summary.forbidden_clean_cases == 1
    assert (
        summary.forbidden_document_absence_rate
        == 1.0
    )
