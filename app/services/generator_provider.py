from app.services.generator import Generator
from app.services.provider_errors import ProviderUnavailableError


def get_generator() -> Generator:
    raise ProviderUnavailableError(
        "Generator provider is not configured."
    )