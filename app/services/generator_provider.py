from app.services.generator import Generator


def get_generator() -> Generator:
    raise RuntimeError(
        "Generator provider is not configured."
    )
