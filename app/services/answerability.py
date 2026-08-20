from dataclasses import dataclass

from app.services.context_builder import RagContext


@dataclass(frozen=True)
class AnswerabilityDecision:
    should_abstain: bool
    reason: str


def assess_answerability(
    context: RagContext,
) -> AnswerabilityDecision:
    if not context.evidence:
        return AnswerabilityDecision(
            should_abstain=True,
            reason="no_context",
        )

    return AnswerabilityDecision(
        should_abstain=False,
        reason="semantic_evaluation_required",
    )
