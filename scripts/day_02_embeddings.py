from sentence_transformers import SentenceTransformer, util
import numpy as np


# ============================================================
# Dia 2 — Embeddings e busca por similaridade
# ============================================================
#
# Objetivo:
# - Transformar chunks de texto em embeddings.
# - Transformar uma pergunta em embedding.
# - Comparar pergunta vs. chunks usando similaridade de cosseno.
# - Retornar o chunk mais relevante.
#
# Observação:
# Este script ainda roda tudo em memória.
# Não usa PostgreSQL, API, pgvector nem LLM.
# ============================================================


# ============================================================
# 1. Chunks de entrada
# ============================================================
#
# Por enquanto usamos chunks de exemplo para validar o fluxo.
#
# TROCAR AQUI PELOS CHUNKS REAIS DO DIA 1:
# Quando os chunks reais estiverem prontos, substitua esta lista
# pela lista gerada no Dia 1.
#
# Exemplo esperado:
#
# chunks = [
#     "chunk real 1 vindo do Dia 1",
#     "chunk real 2 vindo do Dia 1",
#     "chunk real 3 vindo do Dia 1",
# ]
# ============================================================

chunks = [
    "Para fazer login no sistema, acesse a página inicial, informe seu e-mail e senha, e clique no botão Entrar.",
    "Para redefinir sua senha, clique em Esqueci minha senha e siga as instruções enviadas por e-mail.",
    "O relatório financeiro pode ser exportado em formato PDF ou CSV pela área de relatórios.",
    "Administradores podem criar novos usuários acessando o menu de configurações da organização.",
]


# ============================================================
# 2. Pergunta de teste
# ============================================================
#
# Use uma pergunta cuja resposta esteja claramente em um chunk.
# Isso permite validar se o argmax encontra o trecho correto.
# ============================================================

pergunta = "Como faço login?"


# ============================================================
# 3. Carregar modelo de embeddings
# ============================================================
#
# all-MiniLM-L6-v2 gera embeddings com 384 dimensões.
# Cada texto vira uma lista de números que representa seu significado.
# ============================================================

modelo = SentenceTransformer("all-MiniLM-L6-v2")


# ============================================================
# 4. Gerar embeddings dos chunks
# ============================================================
#
# embeddings terá o formato:
# número de chunks x tamanho do vetor
#
# Exemplo:
# 4 chunks x 384 dimensões
# ============================================================

embeddings = modelo.encode(chunks)


# ============================================================
# 5. Gerar embedding da pergunta
# ============================================================
#
# A pergunta também precisa virar vetor para ser comparada
# com os vetores dos chunks.
# ============================================================

pergunta_embedding = modelo.encode(pergunta)


# ============================================================
# 6. Calcular similaridade de cosseno
# ============================================================
#
# cos_sim compara o embedding da pergunta com todos os embeddings
# dos chunks.
#
# Quanto mais próximo de 1, mais semanticamente parecido.
# ============================================================

scores = util.cos_sim(pergunta_embedding, embeddings)


# ============================================================
# 7. Encontrar o chunk mais relevante
# ============================================================
#
# np.argmax retorna o índice do maior score.
# Esse índice aponta para o chunk mais parecido com a pergunta.
# ============================================================

indice_vencedor = int(np.argmax(scores))

chunk_vencedor = chunks[indice_vencedor]
score_vencedor = float(scores[0][indice_vencedor])


# ============================================================
# 8. Exibir resultado
# ============================================================

print("Pergunta:")
print(pergunta)

print("\nÍndice do chunk vencedor:")
print(indice_vencedor)

print("\nChunk mais relevante:")
print(chunk_vencedor)

print("\nScore:")
print(score_vencedor)