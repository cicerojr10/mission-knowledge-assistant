from app.services.answerability import AnswerabilityDecision
from app.services.generator import (
    GenerationResult,
    Generator,
    generate_answer,
)


def generate_if_allowed(
    decision: AnswerabilityDecision,
    generator: Generator,
    question: str,
    context: str,
) -> GenerationResult | None:
    if not decision.can_generate:
        return None

    return generate_answer(
        generator=generator,
        question=question,
        context=context,
    )
