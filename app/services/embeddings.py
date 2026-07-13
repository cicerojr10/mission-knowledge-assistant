from collections.abc import Sequence
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Carrega e mantém uma única instância do modelo por processo.

    A primeira chamada carrega o modelo. As chamadas seguintes
    reutilizam a mesma instância.
    """
    return SentenceTransformer(MODEL_NAME)


def generate_embeddings(texts: Sequence[str]) -> list[list[float]]:
    """
    Gera embeddings para uma sequência de textos.

    Retorna uma lista de vetores, cada um com 384 dimensões.
    """
    text_list = list(texts)

    if not text_list:
        return []

    if any(not text.strip() for text in text_list):
        raise ValueError("Embedding texts must not be empty or blank.")

    model = get_embedding_model()

    embedding_matrix = np.asarray(
        model.encode(
            text_list,
            convert_to_numpy=True,
            show_progress_bar=False,
        ),
        dtype=np.float32,
    )

    expected_shape = (len(text_list), EMBEDDING_DIMENSION)

    if embedding_matrix.shape != expected_shape:
        raise ValueError(
            "Unexpected embedding matrix shape: "
            f"expected {expected_shape}, got {embedding_matrix.shape}."
        )

    return embedding_matrix.tolist()


def generate_embedding(text: str) -> list[float]:
    """
    Gera um único embedding de 384 dimensões.
    """
    return generate_embeddings([text])[0]