from evaluation.models import (
    EvaluationCase,
    EvaluationCategory,
    EvaluationObservation,
)
from evaluation.runner import (
    evaluate_case,
    run_evaluation,
)


def create_case() -> EvaluationCase:
    return EvaluationCase(
        id="case-001",
        category=EvaluationCategory.ANSWERABLE,
        owner_key="primary",
        question="What is documented?",
        expected_abstained=False,
        expected_document_keys=("doc-a",),
        forbidden_document_keys=("doc-secret",),
        reference_answer="Expected answer.",
    )


def test_evaluate_case_passes_when_observation_matches():
    case = create_case()

    observation = EvaluationObservation(
        abstained=False,
        document_keys=("doc-a",),
        answer="Observed answer.",
    )

    result = evaluate_case(
        case=case,
        observation=observation,
    )

    assert result.passed is True
    assert result.abstention_matches is True
    assert result.expected_documents_found is True
    assert result.forbidden_documents_absent is True


def test_evaluate_case_fails_when_expected_document_missing():
    case = create_case()

    observation = EvaluationObservation(
        abstained=False,
        document_keys=(),
        answer="Observed answer.",
    )

    result = evaluate_case(
        case=case,
        observation=observation,
    )

    assert result.passed is False
    assert result.abstention_matches is True
    assert result.expected_documents_found is False
    assert result.forbidden_documents_absent is True


def test_evaluate_case_fails_when_forbidden_document_is_observed():
    case = create_case()

    observation = EvaluationObservation(
        abstained=False,
        document_keys=(
            "doc-a",
            "doc-secret",
        ),
        answer="Observed answer.",
    )

    result = evaluate_case(
        case=case,
        observation=observation,
    )

    assert result.passed is False
    assert result.expected_documents_found is True
    assert result.forbidden_documents_absent is False


def test_run_evaluation_executes_each_case():
    first_case = create_case()

    second_case = EvaluationCase(
        id="case-002",
        category=EvaluationCategory.UNANSWERABLE,
        owner_key="primary",
        question="Unknown information?",
        expected_abstained=True,
        expected_document_keys=(),
        forbidden_document_keys=(),
    )

    observed_case_ids: list[str] = []

    def executor(
        case: EvaluationCase,
    ) -> EvaluationObservation:
        observed_case_ids.append(case.id)

        return EvaluationObservation(
            abstained=case.expected_abstained,
            document_keys=(
                case.expected_document_keys
            ),
        )

    results = run_evaluation(
        cases=[
            first_case,
            second_case,
        ],
        executor=executor,
    )

    assert observed_case_ids == [
        "case-001",
        "case-002",
    ]

    assert len(results) == 2
    assert all(
        result.passed
        for result in results
    )
