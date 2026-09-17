from types import SimpleNamespace

from app.services.answerability import (
    AnswerabilityDecision,
)
from app.services.context_builder import RagContext
from app.services.semantic_answerability import (
    SemanticAnswerabilityRequest,
)
from evaluation.answerability_evaluation import (
    evaluate_answerability_case,
)
from evaluation.models import (
    EvaluationCase,
    EvaluationCategory,
)


class FakeSemanticEvaluator:
    def __init__(
        self,
        decision: AnswerabilityDecision,
    ):
        self.decision = decision
        self.received_request = None

    def evaluate(
        self,
        request: SemanticAnswerabilityRequest,
    ) -> AnswerabilityDecision:
        self.received_request = request
        return self.decision


def create_case(
    *,
    expected_abstained: bool,
) -> EvaluationCase:
    return EvaluationCase(
        id="case-001",
        category=EvaluationCategory.ANSWERABLE,
        owner_key="primary",
        question="What does the evidence support?",
        expected_abstained=expected_abstained,
        expected_document_keys=(),
        forbidden_document_keys=(),
    )


def create_context() -> RagContext:
    return RagContext(
        text="Authorized evidence.",
        evidence=(SimpleNamespace(),),
    )


def test_no_context_abstention_is_evaluated():
    result = evaluate_answerability_case(
        case=create_case(
            expected_abstained=True,
        ),
        context=RagContext(
            text="",
            evidence=(),
        ),
    )

    assert result.evaluated is True
    assert result.expected_abstained is True
    assert result.observed_abstained is True
    assert result.should_abstain is True
    assert result.can_generate is False
    assert result.reason == "no_context"
    assert result.semantic_evaluation_used is False
    assert result.passed is True


def test_semantic_requirement_without_evaluator_is_not_evaluated():
    result = evaluate_answerability_case(
        case=create_case(
            expected_abstained=False,
        ),
        context=create_context(),
    )

    assert result.evaluated is False
    assert result.expected_abstained is False
    assert result.observed_abstained is None
    assert result.should_abstain is None
    assert result.can_generate is None
    assert (
        result.reason
        == "semantic_evaluation_required"
    )
    assert result.semantic_evaluation_used is False
    assert result.passed is None


def test_controlled_semantic_allow_matches_answerable_case():
    evaluator = FakeSemanticEvaluator(
        AnswerabilityDecision(
            should_abstain=False,
            can_generate=True,
            reason="semantic_evaluation_passed",
        )
    )

    context = create_context()

    result = evaluate_answerability_case(
        case=create_case(
            expected_abstained=False,
        ),
        context=context,
        evaluator=evaluator,
    )

    assert result.evaluated is True
    assert result.observed_abstained is False
    assert result.should_abstain is False
    assert result.can_generate is True
    assert result.semantic_evaluation_used is True
    assert result.passed is True

    assert evaluator.received_request == (
        SemanticAnswerabilityRequest(
            question="What does the evidence support?",
            context=context.text,
        )
    )


def test_controlled_semantic_abstention_matches_expected_case():
    evaluator = FakeSemanticEvaluator(
        AnswerabilityDecision(
            should_abstain=True,
            can_generate=False,
            reason="insufficient_semantic_evidence",
        )
    )

    result = evaluate_answerability_case(
        case=create_case(
            expected_abstained=True,
        ),
        context=create_context(),
        evaluator=evaluator,
    )

    assert result.evaluated is True
    assert result.observed_abstained is True
    assert result.should_abstain is True
    assert result.can_generate is False
    assert result.semantic_evaluation_used is True
    assert result.passed is True


def test_controlled_semantic_decision_can_fail_expectation():
    evaluator = FakeSemanticEvaluator(
        AnswerabilityDecision(
            should_abstain=False,
            can_generate=True,
            reason="semantic_evaluation_passed",
        )
    )

    result = evaluate_answerability_case(
        case=create_case(
            expected_abstained=True,
        ),
        context=create_context(),
        evaluator=evaluator,
    )

    assert result.evaluated is True
    assert result.observed_abstained is False
    assert result.passed is False