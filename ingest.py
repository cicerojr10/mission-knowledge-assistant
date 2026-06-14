import os
from sentence_transformers import SentenceTransformer, util
import ollama  # 👈 NOVO


# Pasta onde estão os documentos
PASTA_DADOS = "data"

# Modelo de embeddings (baixa automático na primeira vez)
MODELO = SentenceTransformer("all-MiniLM-L6-v2")


def carregar_documentos(pasta):
    """Lê todos os arquivos .txt da pasta e retorna uma lista de dicionários."""
    documentos = []

    for nome_arquivo in os.listdir(pasta):
        if nome_arquivo.endswith(".txt"):
            caminho = os.path.join(pasta, nome_arquivo)

            with open(caminho, "r", encoding="utf-8") as f:
                conteudo = f.read()

            documentos.append({
                "fonte": nome_arquivo,
                "texto": conteudo
            })
            print(f"✅ Carregado: {nome_arquivo} ({len(conteudo)} caracteres)")

    return documentos


def dividir_em_chunks(texto, tamanho_chunk=500, overlap=100):
    """Divide um texto em chunks com sobreposição (overlap)."""
    chunks = []
    inicio = 0

    while inicio < len(texto):
        fim = inicio + tamanho_chunk
        chunk = texto[inicio:fim]
        chunks.append(chunk.strip())
        inicio += tamanho_chunk - overlap

    return chunks


def gerar_embeddings(chunks):
    """Recebe a lista de chunks e adiciona o vetor de embedding em cada um."""
    textos = [c["texto"] for c in chunks]
    vetores = MODELO.encode(textos)

    for chunk, vetor in zip(chunks, vetores):
        chunk["embedding"] = vetor

    print(f"🧬 {len(vetores)} embeddings gerados (dimensão: {len(vetores[0])})")
    return chunks


def buscar(pergunta, chunks, top_k=3):
    """Busca os chunks mais relevantes para a pergunta."""
    emb_pergunta = MODELO.encode(pergunta)

    for chunk in chunks:
        chunk["score"] = float(
            util.cos_sim(emb_pergunta, chunk["embedding"])[0][0]
        )

    ranqueados = sorted(chunks, key=lambda c: c["score"], reverse=True)
    return ranqueados[:top_k]


# ============================================================
# 👇 FUNÇÕES NOVAS
# ============================================================

def montar_prompt(pergunta, resultados):
    """Junta os chunks recuperados + a pergunta num único prompt."""
    contexto = "\n\n".join(
        f"[{r['fonte']}] {r['texto']}" for r in resultados
    )

    prompt = f"""Use APENAS o contexto abaixo para responder em português.
Se a resposta não estiver no contexto, diga que não sabe.

### Contexto:
{contexto}

### Pergunta:
{pergunta}

### Resposta:"""

    return prompt


def gerar_resposta(prompt, modelo="llama3.2"):
    """Envia o prompt ao Ollama e retorna a resposta gerada pelo LLM local."""
    resposta = ollama.chat(
        model=modelo,
        messages=[{"role": "user", "content": prompt}]
    )
    return resposta["message"]["content"]


if __name__ == "__main__":
    # 1) Carrega documentos
    docs = carregar_documentos(PASTA_DADOS)
    print(f"\n📚 Total de documentos carregados: {len(docs)}\n")

    # 2) Divide em chunks
    todos_os_chunks = []
    for doc in docs:
        chunks = dividir_em_chunks(doc["texto"])
        print(f"📄 {doc['fonte']} → {len(chunks)} chunk(s)")

        for i, chunk in enumerate(chunks):
            todos_os_chunks.append({
                "fonte": doc["fonte"],
                "chunk_id": i,
                "texto": chunk
            })

    print(f"\n✂️  Total de chunks gerados: {len(todos_os_chunks)}")

    # 3) Gera embeddings (PRECISA vir antes da busca!)
    todos_os_chunks = gerar_embeddings(todos_os_chunks)

    # 4) Busca por similaridade
    print("\n" + "=" * 50)
    pergunta = "O que são embeddings?"
    print(f"❓ Pergunta: {pergunta}\n")

    resultados = buscar(pergunta, todos_os_chunks)

    for i, r in enumerate(resultados, 1):
        print(f"🥇 #{i} | score: {r['score']:.4f} | fonte: {r['fonte']}")
        print(f"   {r['texto'][:120]}...\n")

    # 5) 👇 NOVO: Monta o prompt e gera a resposta com o Ollama
    prompt_final = montar_prompt(pergunta, resultados)

    print("=" * 50)
    print("🤖 Gerando resposta com o Ollama...\n")
    resposta = gerar_resposta(prompt_final)
    print(f"💬 Resposta:\n{resposta}")
