import openai
import pytest
from pydantic import SecretStr

from app.config import settings
from app.services.openai_semantic_answerability import (
    OpenAISemanticAnswerabilityEvaluator,
)
from app.services.provider_errors import ProviderUnavailableError
from app.services.semantic_answerability_provider import (
    get_semantic_answerability_evaluator,
)


def test_provider_builds_openai_evaluator_when_configured(
    monkeypatch,
):
    fake_client = object()
    captured = {}

    def fake_openai(*, api_key):
        captured["api_key"] = api_key
        return fake_client

    monkeypatch.setattr(
        settings,
        "openai_api_key",
        SecretStr("test-only-api-key"),
    )
    monkeypatch.setattr(
        settings,
        "openai_answerability_model",
        "test-model",
    )
    monkeypatch.setattr(
        openai,
        "OpenAI",
        fake_openai,
    )

    evaluator = get_semantic_answerability_evaluator()

    assert isinstance(
        evaluator,
        OpenAISemanticAnswerabilityEvaluator,
    )
    assert evaluator.client is fake_client
    assert evaluator.model == "test-model"
    assert captured["api_key"] == "test-only-api-key"


def test_provider_returns_none_when_configuration_is_incomplete(
    monkeypatch,
):
    def fail_if_client_is_created(**kwargs):
        raise AssertionError(
            "OpenAI client must not be created."
        )

    monkeypatch.setattr(
        openai,
        "OpenAI",
        fail_if_client_is_created,
    )

    configurations = [
        (None, None),
        (None, "test-model"),
        (SecretStr("test-only-api-key"), None),
    ]

    for api_key, model in configurations:
        monkeypatch.setattr(
            settings,
            "openai_api_key",
            api_key,
        )
        monkeypatch.setattr(
            settings,
            "openai_answerability_model",
            model,
        )

        evaluator = get_semantic_answerability_evaluator()

        assert evaluator is None


def test_provider_maps_openai_client_initialization_failure(
    monkeypatch,
):
    def fake_openai(*, api_key):
        raise openai.OpenAIError(
            "internal simulated initialization failure"
        )

    monkeypatch.setattr(
        settings,
        "openai_api_key",
        SecretStr("test-only-api-key"),
    )
    monkeypatch.setattr(
        settings,
        "openai_answerability_model",
        "test-model",
    )
    monkeypatch.setattr(
        openai,
        "OpenAI",
        fake_openai,
    )

    with pytest.raises(
        ProviderUnavailableError,
        match="OpenAI answerability client initialization failed",
    ) as exc_info:
        get_semantic_answerability_evaluator()

    assert (
        "internal simulated initialization failure"
        not in str(exc_info.value)
    )
