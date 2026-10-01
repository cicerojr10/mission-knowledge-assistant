from types import SimpleNamespace

import pytest

from app.services.answerability import AnswerabilityDecision
from app.services.openai_semantic_answerability import (
    OpenAISemanticAnswerabilityEvaluator,
)
from app.services.provider_errors import ProviderUnavailableError
from app.services.semantic_answerability import (
    SemanticAnswerabilityRequest,
)


class FakeResponses:
    def __init__(self, *, answerable: bool, reason: str):
        self.answerable = answerable
        self.reason = reason
        self.received_kwargs = None

    def parse(self, **kwargs):
        self.received_kwargs = kwargs

        return SimpleNamespace(
            output_parsed=SimpleNamespace(
                answerable=self.answerable,
                reason=self.reason,
            )
        )


class FakeOpenAIClient:
    def __init__(self, *, answerable: bool, reason: str):
        self.responses = FakeResponses(
            answerable=answerable,
            reason=reason,
        )


class FakeResponsesWithoutParsedOutput:
    def parse(self, **kwargs):
        return SimpleNamespace(
            output_parsed=None,
        )


class FakeOpenAIClientWithoutParsedOutput:
    def __init__(self):
        self.responses = FakeResponsesWithoutParsedOutput()


def test_openai_answerability_passes_question_and_context_to_provider():
    client = FakeOpenAIClient(
        answerable=True,
        reason="The context directly supports the answer.",
    )

    evaluator = OpenAISemanticAnswerabilityEvaluator(
        client=client,
        model="test-model",
    )

    decision = evaluator.evaluate(
        SemanticAnswerabilityRequest(
            question="Why was the contract cancelled?",
            context=(
                "The contract was cancelled because "
                "funding ended."
            ),
        )
    )

    assert client.responses.received_kwargs is not None

    assert (
        client.responses.received_kwargs["model"]
        == "test-model"
    )

    provider_input = str(
        client.responses.received_kwargs["input"]
    )

    assert "Why was the contract cancelled?" in provider_input
    assert "funding ended" in provider_input

    assert decision == AnswerabilityDecision(
        should_abstain=False,
        can_generate=True,
        reason="semantic_evaluation_passed",
    )


def test_openai_answerability_maps_negative_result_to_abstention():
    client = FakeOpenAIClient(
        answerable=False,
        reason=(
            "The context does not contain enough "
            "evidence."
        ),
    )

    evaluator = OpenAISemanticAnswerabilityEvaluator(
        client=client,
        model="test-model",
    )

    decision = evaluator.evaluate(
        SemanticAnswerabilityRequest(
            question="What was the final contract value?",
            context=(
                "The contract was cancelled because "
                "funding ended."
            ),
        )
    )

    assert decision == AnswerabilityDecision(
        should_abstain=True,
        can_generate=False,
        reason="semantic_evaluation_failed",
    )


def test_openai_answerability_rejects_missing_structured_output():
    evaluator = OpenAISemanticAnswerabilityEvaluator(
        client=FakeOpenAIClientWithoutParsedOutput(),
        model="test-model",
    )

    request = SemanticAnswerabilityRequest(
        question="What was the final contract value?",
        context="The contract was cancelled.",
    )

    with pytest.raises(ProviderUnavailableError):
        evaluator.evaluate(request)
