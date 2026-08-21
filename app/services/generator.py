from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class GenerationRequest:
    question: str
    context: str


@dataclass(frozen=True)
class GenerationResult:
    text: str


class Generator(Protocol):
    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        ...


def generate_answer(
    generator: Generator,
    question: str,
    context: str,
) -> GenerationResult:
    request = GenerationRequest(
        question=question,
        context=context,
    )

    return generator.generate(request)
