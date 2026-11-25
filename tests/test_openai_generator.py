from types import SimpleNamespace

import httpx2
import pytest
from openai import APIConnectionError, RateLimitError

from app.services.generator import (
    GenerationRequest,
    GenerationResult,
)
from app.services.openai_generator import OpenAIGenerator
from app.services.provider_errors import ProviderUnavailableError


class FakeResponses:
    def __init__(self):
        self.received_kwargs = None

    def create(self, **kwargs):
        self.received_kwargs = kwargs

        return SimpleNamespace(
            output_text="The document requires owner filtering."
        )


class FakeOpenAIClient:
    def __init__(self):
        self.responses = FakeResponses()


def test_openai_generator_passes_question_and_context():
    client = FakeOpenAIClient()

    generator = OpenAIGenerator(
        client=client,
        model="test-model",
    )

    result = generator.generate(
        GenerationRequest(
            question="What does the document require?",
            context=(
                "The document requires owner filtering."
            ),
        )
    )

    received = client.responses.received_kwargs

    assert received is not None
    assert received["model"] == "test-model"

    provider_input = str(received["input"])

    assert "What does the document require?" in provider_input
    assert "The document requires owner filtering." in provider_input

    assert result == GenerationResult(
        text="The document requires owner filtering."
    )


def test_openai_generator_maps_connection_error(
    monkeypatch,
):
    client = FakeOpenAIClient()

    def fake_create(**kwargs):
        request = httpx2.Request(
            "POST",
            "https://api.openai.com/v1/responses",
        )

        raise APIConnectionError(
            request=request,
        )

    monkeypatch.setattr(
        client.responses,
        "create",
        fake_create,
    )

    generator = OpenAIGenerator(
        client=client,
        model="test-model",
    )

    request = GenerationRequest(
        question="What happened?",
        context="Authorized document context.",
    )

    with pytest.raises(ProviderUnavailableError):
        generator.generate(request)


def test_openai_generator_maps_rate_limit_error(
    monkeypatch,
):
    client = FakeOpenAIClient()

    def fake_create(**kwargs):
        request = httpx2.Request(
            "POST",
            "https://api.openai.com/v1/responses",
        )

        response = httpx2.Response(
            status_code=429,
            request=request,
        )

        raise RateLimitError(
            "Rate limit exceeded.",
            response=response,
            body=None,
        )

    monkeypatch.setattr(
        client.responses,
        "create",
        fake_create,
    )

    generator = OpenAIGenerator(
        client=client,
        model="test-model",
    )

    request = GenerationRequest(
        question="What happened?",
        context="Authorized document context.",
    )

    with pytest.raises(ProviderUnavailableError):
        generator.generate(request)
