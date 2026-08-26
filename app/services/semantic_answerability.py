from dataclasses import dataclass
from typing import Protocol

from app.services.answerability import AnswerabilityDecision


@dataclass(frozen=True)
class SemanticAnswerabilityRequest:
    question: str
    context: str


class SemanticAnswerabilityEvaluator(Protocol):
    def evaluate(
        self,
        request: SemanticAnswerabilityRequest,
    ) -> AnswerabilityDecision:
        ...


def evaluate_semantic_answerability(
    evaluator: SemanticAnswerabilityEvaluator,
    question: str,
    context: str,
) -> AnswerabilityDecision:
    request = SemanticAnswerabilityRequest(
        question=question,
        context=context,
    )

    return evaluator.evaluate(request)
