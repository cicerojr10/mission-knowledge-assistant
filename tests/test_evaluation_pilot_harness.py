from pathlib import Path

from evaluation.dataset import load_evaluation_cases
from evaluation.metrics import (
    summarize_results,
    summarize_results_by_category,
)
from evaluation.models import (
    EvaluationCase,
    EvaluationCategory,
    EvaluationObservation,
)
from evaluation.runner import run_evaluation


DATA_DIRECTORY = (
    Path(__file__).resolve().parents[1]
    / "evaluation"
    / "data"
)


def controlled_executor(
    case: EvaluationCase,
) -> EvaluationObservation:
    return EvaluationObservation(
        abstained=case.expected_abstained,
        document_keys=case.expected_document_keys,
        answer=case.reference_answer,
    )


def test_pilot_harness_runs_all_cases():
    cases = load_evaluation_cases(
        DATA_DIRECTORY / "cases.jsonl"
    )

    results = run_evaluation(
        cases=cases,
        executor=controlled_executor,
    )

    summary = summarize_results(results)

    assert summary.total_cases == 8
    assert summary.passed_cases == 8
    assert summary.pass_rate == 1.0
    assert summary.abstention_match_rate == 1.0
    assert (
        summary.expected_documents_found_rate
        == 1.0
    )
    assert (
        summary.forbidden_documents_absent_rate
        == 1.0
    )


def test_pilot_harness_preserves_category_counts():
    cases = load_evaluation_cases(
        DATA_DIRECTORY / "cases.jsonl"
    )

    results = run_evaluation(
        cases=cases,
        executor=controlled_executor,
    )

    summaries = summarize_results_by_category(
        results
    )

    assert summaries[
        EvaluationCategory.ANSWERABLE
    ].total_cases == 3

    assert summaries[
        EvaluationCategory.UNANSWERABLE
    ].total_cases == 2

    assert summaries[
        EvaluationCategory.CROSS_USER
    ].total_cases == 2

    assert summaries[
        EvaluationCategory.DIFFICULT
    ].total_cases == 1
