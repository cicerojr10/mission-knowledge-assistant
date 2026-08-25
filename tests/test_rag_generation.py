from app.services.answerability import AnswerabilityDecision
from app.services.generator import (
    GenerationRequest,
    GenerationResult,
)
from app.services.rag_generation import generate_if_allowed


class FakeGenerator:
    def __init__(self):
        self.received_request = None

    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        self.received_request = request

        return GenerationResult(
            text="Grounded answer.",
        )


def test_generate_if_allowed_skips_generator_when_not_allowed():
    generator = FakeGenerator()

    decision = AnswerabilityDecision(
        should_abstain=False,
        can_generate=False,
        reason="semantic_evaluation_required",
    )

    result = generate_if_allowed(
        decision=decision,
        generator=generator,
        question="What happened?",
        context="Authorized context.",
    )

    assert result is None
    assert generator.received_request is None


def test_generate_if_allowed_calls_generator_when_allowed():
    generator = FakeGenerator()

    decision = AnswerabilityDecision(
        should_abstain=False,
        can_generate=True,
        reason="semantic_evaluation_passed",
    )

    result = generate_if_allowed(
        decision=decision,
        generator=generator,
        question="What happened?",
        context="Authorized context.",
    )

    assert generator.received_request == GenerationRequest(
        question="What happened?",
        context="Authorized context.",
    )

    assert result == GenerationResult(
        text="Grounded answer.",
    )
