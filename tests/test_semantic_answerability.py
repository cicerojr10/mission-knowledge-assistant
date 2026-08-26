from app.services.answerability import AnswerabilityDecision
from app.services.semantic_answerability import (
    SemanticAnswerabilityEvaluator,
    SemanticAnswerabilityRequest,
    evaluate_semantic_answerability,
)


class FakeSemanticAnswerabilityEvaluator:
    def __init__(self):
        self.received_request = None

    def evaluate(
        self,
        request: SemanticAnswerabilityRequest,
    ) -> AnswerabilityDecision:
        self.received_request = request

        return AnswerabilityDecision(
            should_abstain=False,
            can_generate=True,
            reason="semantic_evaluation_passed",
        )


def test_semantic_answerability_passes_question_and_context_to_evaluator():
    evaluator: SemanticAnswerabilityEvaluator = (
        FakeSemanticAnswerabilityEvaluator()
    )

    decision = evaluate_semantic_answerability(
        evaluator=evaluator,
        question="Why was the contract cancelled?",
        context="The contract was cancelled because funding ended.",
    )

    assert evaluator.received_request == SemanticAnswerabilityRequest(
        question="Why was the contract cancelled?",
        context="The contract was cancelled because funding ended.",
    )

    assert decision == AnswerabilityDecision(
        should_abstain=False,
        can_generate=True,
        reason="semantic_evaluation_passed",
    )
