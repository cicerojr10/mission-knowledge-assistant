import openai

from app.config import settings
from app.services.openai_semantic_answerability import (
    OpenAISemanticAnswerabilityEvaluator,
)
from app.services.provider_errors import ProviderUnavailableError
from app.services.semantic_answerability import (
    SemanticAnswerabilityEvaluator,
)


def get_semantic_answerability_evaluator(
) -> SemanticAnswerabilityEvaluator | None:
    api_key = settings.openai_api_key
    model = settings.openai_answerability_model

    if api_key is None or model is None:
        return None

    try:
        client = openai.OpenAI(
            api_key=api_key.get_secret_value(),
        )
    except openai.OpenAIError as exc:
        raise ProviderUnavailableError(
            "OpenAI answerability client initialization failed."
        ) from exc

    return OpenAISemanticAnswerabilityEvaluator(
        client=client,
        model=model,
    )
