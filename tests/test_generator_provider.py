from types import SimpleNamespace

import openai
import pytest
from pydantic import SecretStr

import app.services.generator_provider as provider
from app.config import settings
from app.services.openai_generator import OpenAIGenerator
from app.services.provider_errors import ProviderUnavailableError


@pytest.mark.parametrize(
    "api_key, model",
    [
        (None, None),
        (None, "test-model"),
        (SecretStr("test-key"), None),
    ],
)
def test_get_generator_rejects_missing_configuration(
    monkeypatch,
    api_key,
    model,
):
    monkeypatch.setattr(
        settings,
        "openai_api_key",
        api_key,
    )
    monkeypatch.setattr(
        settings,
        "openai_generation_model",
        model,
    )

    def unexpected_client_initialization(**kwargs):
        pytest.fail(
            "Client must not be initialized "
            "without complete configuration."
        )

    monkeypatch.setattr(
        provider.openai,
        "OpenAI",
        unexpected_client_initialization,
    )

    with pytest.raises(ProviderUnavailableError):
        provider.get_generator()


def test_get_generator_returns_configured_openai_generator(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "openai_api_key",
        SecretStr("test-key"),
    )
    monkeypatch.setattr(
        settings,
        "openai_generation_model",
        "test-generation-model",
    )

    fake_client = SimpleNamespace()
    captured = {}

    def fake_openai_client(**kwargs):
        captured.update(kwargs)
        return fake_client

    monkeypatch.setattr(
        provider.openai,
        "OpenAI",
        fake_openai_client,
    )

    generator = provider.get_generator()

    assert isinstance(generator, OpenAIGenerator)
    assert generator.client is fake_client
    assert generator.model == "test-generation-model"
    assert captured["api_key"] == "test-key"


def test_get_generator_maps_client_initialization_error(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "openai_api_key",
        SecretStr("test-key"),
    )
    monkeypatch.setattr(
        settings,
        "openai_generation_model",
        "test-model",
    )

    def failing_openai_client(**kwargs):
        raise openai.OpenAIError(
            "Client initialization failed."
        )

    monkeypatch.setattr(
        provider.openai,
        "OpenAI",
        failing_openai_client,
    )

    with pytest.raises(ProviderUnavailableError) as exc_info:
        provider.get_generator()

    assert isinstance(
        exc_info.value.__cause__,
        openai.OpenAIError,
    )
