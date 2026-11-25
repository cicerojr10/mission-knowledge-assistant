import openai

from app.config import settings
from app.services.generator import Generator
from app.services.openai_generator import OpenAIGenerator
from app.services.provider_errors import ProviderUnavailableError


def get_generator() -> Generator:
    api_key = settings.openai_api_key
    model = settings.openai_generation_model

    if api_key is None or model is None:
        raise ProviderUnavailableError(
            "OpenAI generation provider is not configured."
        )

    try:
        client = openai.OpenAI(
            api_key=api_key.get_secret_value(),
        )
    except openai.OpenAIError as exc:
        raise ProviderUnavailableError(
            "OpenAI generation client initialization failed."
        ) from exc

    return OpenAIGenerator(
        client=client,
        model=model,
    )
