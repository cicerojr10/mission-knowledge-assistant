def split_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """
    Divide um texto em chunks de tamanho fixo com overlap.

    Esta função ainda não salva nada no banco.
    Ela apenas transforma um texto completo em uma lista de trechos.

    Exemplo:
    - chunk_size=500
    - overlap=50

    O próximo chunk começa 50 caracteres antes do fim do chunk anterior,
    preservando um pequeno contexto entre os trechos.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0:
        raise ValueError("overlap must be greater than or equal to zero.")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    clean_text = text.strip()

    if not clean_text:
        return []

    chunks: list[str] = []
    start = 0
    text_length = len(clean_text)

    while start < text_length:
        end = start + chunk_size
        chunk = clean_text[start:end]

        chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks