from sentence_transformers import SentenceTransformer
import numpy as np


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """
    Calcula similaridade de cosseno entre dois vetores.

    Quanto mais perto de 1.0, mais parecidos semanticamente
    os textos tendem a ser.
    """
    dot_product = np.dot(vector_a, vector_b)
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)

    return dot_product / (norm_a * norm_b)


def main() -> None:
    model = SentenceTransformer(MODEL_NAME)

    sentences = [
        "Artemis is a NASA program focused on returning humans to the Moon.",
        "NASA wants to send astronauts back to the lunar surface.",
        "PostgreSQL is a relational database used by backend applications.",
    ]

    embeddings = model.encode(sentences)

    print(f"Model: {MODEL_NAME}")
    print(f"Embedding matrix shape: {embeddings.shape}")
    print(f"Embedding dimensions: {embeddings.shape[1]}")

    similarity_related = cosine_similarity(embeddings[0], embeddings[1])
    similarity_unrelated = cosine_similarity(embeddings[0], embeddings[2])

    print()
    print("Semantic similarity examples:")
    print(f"Artemis / lunar mission: {similarity_related:.4f}")
    print(f"Artemis / PostgreSQL: {similarity_unrelated:.4f}")

    if embeddings.shape[1] != 384:
        raise ValueError("Expected embeddings with 384 dimensions.")

    if similarity_related <= similarity_unrelated:
        raise ValueError(
            "Expected related sentences to be more similar than unrelated sentences."
        )

    print()
    print("Embedding validation completed successfully.")


if __name__ == "__main__":
    main()
