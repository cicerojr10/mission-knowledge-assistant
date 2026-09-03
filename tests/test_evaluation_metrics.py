from evaluation.metrics import (
    summarize_results,
    summarize_results_by_category,
)
from evaluation.models import (
    EvaluationCategory,
    EvaluationResult,
)


def create_result(
    *,
    case_id: str,
    category: EvaluationCategory,
    passed: bool,
    abstention_matches: bool = True,
    expected_documents_found: bool = True,
    forbidden_documents_absent: bool = True,
) -> EvaluationResult:
    return EvaluationResult(
        case_id=case_id,
        category=category,
        passed=passed,
        abstention_matches=abstention_matches,
        expected_documents_found=(
            expected_documents_found
        ),
        forbidden_documents_absent=(
            forbidden_documents_absent
        ),
    )


def test_summarize_results_calculates_rates():
    results = [
        create_result(
            case_id="case-001",
            category=EvaluationCategory.ANSWERABLE,
            passed=True,
        ),
        create_result(
            case_id="case-002",
            category=EvaluationCategory.ANSWERABLE,
            passed=False,
            expected_documents_found=False,
        ),
        create_result(
            case_id="case-003",
            category=EvaluationCategory.UNANSWERABLE,
            passed=False,
            abstention_matches=False,
        ),
        create_result(
            case_id="case-004",
            category=EvaluationCategory.CROSS_USER,
            passed=False,
            forbidden_documents_absent=False,
        ),
    ]

    summary = summarize_results(results)

    assert summary.total_cases == 4
    assert summary.passed_cases == 1
    assert summary.pass_rate == 0.25
    assert summary.abstention_match_rate == 0.75
    assert (
        summary.expected_documents_found_rate
        == 0.75
    )
    assert (
        summary.forbidden_documents_absent_rate
        == 0.75
    )


def test_summarize_results_handles_empty_input():
    summary = summarize_results([])

    assert summary.total_cases == 0
    assert summary.passed_cases == 0
    assert summary.pass_rate == 0.0
    assert summary.abstention_match_rate == 0.0
    assert (
        summary.expected_documents_found_rate
        == 0.0
    )
    assert (
        summary.forbidden_documents_absent_rate
        == 0.0
    )


def test_summarize_results_by_category():
    results = [
        create_result(
            case_id="case-001",
            category=EvaluationCategory.ANSWERABLE,
            passed=True,
        ),
        create_result(
            case_id="case-002",
            category=EvaluationCategory.ANSWERABLE,
            passed=False,
            expected_documents_found=False,
        ),
        create_result(
            case_id="case-003",
            category=EvaluationCategory.CROSS_USER,
            passed=True,
        ),
    ]

    summaries = summarize_results_by_category(
        results
    )

    answerable = summaries[
        EvaluationCategory.ANSWERABLE
    ]

    cross_user = summaries[
        EvaluationCategory.CROSS_USER
    ]

    difficult = summaries[
        EvaluationCategory.DIFFICULT
    ]

    assert answerable.total_cases == 2
    assert answerable.passed_cases == 1
    assert answerable.pass_rate == 0.5

    assert cross_user.total_cases == 1
    assert cross_user.pass_rate == 1.0

    assert difficult.total_cases == 0
    assert difficult.pass_rate == 0.0
