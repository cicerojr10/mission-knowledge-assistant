from sentence_transformers import SentenceTransformer, util
import numpy as np


# ============================================================
# Dia 3 — Busca semântica organizada em funções
# ============================================================
#
# Objetivo:
# - Reorganizar o experimento do Dia 2 em funções reutilizáveis.
# - Manter a busca por similaridade funcionando.
# - Preparar a lógica para futura integração com API, testes e banco.
#
# Este script ainda roda tudo em memória.
# Não usa FastAPI, PostgreSQL, pgvector nem LLM.
# ============================================================


MODEL_NAME = "all-MiniLM-L6-v2"


def load_model() -> SentenceTransformer:
    """
    Carrega o modelo de embeddings.

    No trabalho real, carregar o modelo em uma função separada ajuda a evitar
    repetição e facilita reaproveitar essa lógica em outros pontos do projeto.
    """
    return SentenceTransformer(MODEL_NAME)


def generate_embeddings(
    model: SentenceTransformer,
    chunks: list[str],
) -> np.ndarray:
    """
    Gera embeddings para uma lista de chunks.

    Cada chunk de texto é convertido em um vetor numérico.
    Com o modelo all-MiniLM-L6-v2, cada vetor possui 384 dimensões.
    """
    return model.encode(chunks)


def find_most_similar_chunk(
    model: SentenceTransformer,
    question: str,
    chunks: list[str],
    chunk_embeddings: np.ndarray,
) -> tuple[int, str, float]:
    """
    Encontra o chunk mais parecido semanticamente com a pergunta.

    Fluxo:
    1. Transforma a pergunta em embedding.
    2. Compara a pergunta com todos os chunks usando similaridade de cosseno.
    3. Usa argmax para encontrar o maior score.
    4. Retorna índice, texto do chunk e score.
    """
    question_embedding = model.encode(question)

    scores = util.cos_sim(question_embedding, chunk_embeddings)

    best_index = int(np.argmax(scores))
    best_chunk = chunks[best_index]
    best_score = float(scores[0][best_index])

    return best_index, best_chunk, best_score


def main() -> None:
    """
    Executa um teste local de busca semântica.

    Esta função funciona como ponto de entrada do script.
    Ela simula o fluxo mínimo de recuperação usado em RAG.
    """

    # ========================================================
    # Chunks de entrada
    # ========================================================
    #
    # TROCAR AQUI PELOS CHUNKS REAIS DO DIA 1:
    #
    # Quando os chunks reais estiverem prontos, substitua esta
    # lista pelos chunks gerados no Dia 1.
    #
    # Exemplo:
    #
    # chunks = [
    #     "chunk real 1 vindo do Dia 1",
    #     "chunk real 2 vindo do Dia 1",
    #     "chunk real 3 vindo do Dia 1",
    # ]
    # ========================================================

    chunks = [
        "Para fazer login no sistema, acesse a página inicial, informe seu e-mail e senha, e clique no botão Entrar.",
        "Para redefinir sua senha, clique em Esqueci minha senha e siga as instruções enviadas por e-mail.",
        "O relatório financeiro pode ser exportado em formato PDF ou CSV pela área de relatórios.",
        "Administradores podem criar novos usuários acessando o menu de configurações da organização.",
    ]

    question = "Como faço login?"

    model = load_model()
    chunk_embeddings = generate_embeddings(model, chunks)

    best_index, best_chunk, best_score = find_most_similar_chunk(
        model=model,
        question=question,
        chunks=chunks,
        chunk_embeddings=chunk_embeddings,
    )

    print("Pergunta:")
    print(question)

    print("\nÍndice do chunk vencedor:")
    print(best_index)

    print("\nChunk mais relevante:")
    print(best_chunk)

    print("\nScore:")
    print(best_score)


if __name__ == "__main__":
    main()