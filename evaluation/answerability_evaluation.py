from dataclasses import dataclass

from app.services.context_builder import RagContext
from app.services.semantic_answerability import (
    SemanticAnswerabilityEvaluator,
    evaluate_semantic_answerability,
)
from app.services.answerability import (
    assess_answerability,
)
from evaluation.models import EvaluationCase


@dataclass(frozen=True)
class AnswerabilityEvaluationResult:
    evaluated: bool
    expected_abstained: bool
    observed_abstained: bool | None
    should_abstain: bool | None
    can_generate: bool | None
    reason: str
    semantic_evaluation_used: bool
    passed: bool | None


def evaluate_answerability_case(
    case: EvaluationCase,
    context: RagContext,
    evaluator: SemanticAnswerabilityEvaluator | None = None,
) -> AnswerabilityEvaluationResult:
    decision = assess_answerability(context)

    if decision.reason == "semantic_evaluation_required":
        if evaluator is None:
            return AnswerabilityEvaluationResult(
                evaluated=False,
                expected_abstained=case.expected_abstained,
                observed_abstained=None,
                should_abstain=None,
                can_generate=None,
                reason=decision.reason,
                semantic_evaluation_used=False,
                passed=None,
            )

        decision = evaluate_semantic_answerability(
            evaluator=evaluator,
            question=case.question,
            context=context.text,
        )

        semantic_evaluation_used = True
    else:
        semantic_evaluation_used = False

    observed_abstained = not decision.can_generate

    return AnswerabilityEvaluationResult(
        evaluated=True,
        expected_abstained=case.expected_abstained,
        observed_abstained=observed_abstained,
        should_abstain=decision.should_abstain,
        can_generate=decision.can_generate,
        reason=decision.reason,
        semantic_evaluation_used=(
            semantic_evaluation_used
        ),
        passed=(
            observed_abstained
            is case.expected_abstained
        ),
    )