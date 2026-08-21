from app.services.generator import (
    GenerationRequest,
    GenerationResult,
    Generator,
    generate_answer,
)


class FakeGenerator:
    def __init__(self):
        self.received_request = None

    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        self.received_request = request

        return GenerationResult(
            text="Generated answer.",
        )


def test_generate_answer_passes_question_and_context_to_generator():
    generator: Generator = FakeGenerator()

    result = generate_answer(
        generator=generator,
        question="What happened?",
        context="Authorized context.",
    )

    assert generator.received_request == GenerationRequest(
        question="What happened?",
        context="Authorized context.",
    )

    assert result == GenerationResult(
        text="Generated answer.",
    )
