# Mission Knowledge Assistant

Backend para um assistente de conhecimento baseado em documentos, desenvolvido de forma incremental com **Python, FastAPI, PostgreSQL e pgvector**.

O projeto começou com fundamentos de API, persistência e recuperação textual e está evoluindo progressivamente para **busca semântica, recuperação híbrida e aplicações de IA/LLM**.

O objetivo não é apenas adicionar tecnologias, mas construir e validar cada camada separadamente antes de avançar para RAG.

---

## Status atual

**Semana 4 concluída — Retrieval semântico e híbrido**

O backend atualmente possui:

- API REST com FastAPI;
- persistência com PostgreSQL;
- modelagem com SQLModel;
- migrations com Alembic;
- ambiente local com Docker Compose;
- cadastro e listagem de documentos;
- geração automática de chunks;
- relacionamento `Document -> Chunk`;
- embeddings persistidos por chunk;
- busca textual com `ILIKE`;
- busca semântica com pgvector;
- filtro opcional de relevância com `max_distance`;
- busca híbrida com Reciprocal Rank Fusion (RRF);
- experimentos controlados de comparação entre recuperação textual e vetorial;
- testes automatizados com Pytest;
- documentação de decisões arquiteturais e experimentos.

Estado atual da suíte:

```text
54 passed
```

RAG e geração de respostas com LLM **ainda não fazem parte do estado atual**.

---

## Stack

### Backend

- Python
- FastAPI
- SQLModel
- Pydantic

### Dados

- PostgreSQL
- pgvector
- Alembic

### IA / Retrieval

- Sentence Transformers
- `sentence-transformers/all-MiniLM-L6-v2`
- embeddings de 384 dimensões
- cosine distance
- Reciprocal Rank Fusion (RRF)

### Engenharia

- Docker
- Docker Compose
- Pytest
- Git / GitHub
- Architecture Decision Records (ADRs)

---

## Arquitetura atual

O fluxo principal de dados é:

```text
Documento
   ↓
Chunking
   ↓
Chunks persistidos
   ↓
Embeddings de 384 dimensões
   ↓
PostgreSQL + pgvector
   ↓
Retrieval
   ├── busca textual
   ├── busca semântica
   └── busca híbrida com RRF
```

O projeto mantém os mecanismos de recuperação separados para que cada estratégia possa ser testada e comparada individualmente.

---

## Estratégia de chunking

Os documentos são divididos automaticamente em chunks.

Configuração atual:

```text
chunk_size = 500
overlap = 50
```

O chunk é a unidade principal de recuperação e também a unidade associada aos embeddings.

---

## Embeddings

O projeto utiliza localmente:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Cada texto é representado por um vetor com:

```text
384 dimensões
```

Os embeddings são armazenados diretamente no PostgreSQL usando:

```text
vector(384)
```

A geração local foi escolhida nesta etapa para permitir estudo e validação do pipeline completo sem depender de APIs externas.

---

## Endpoints principais

### `GET /health`

Verifica se a API está disponível.

Exemplo:

```json
{
  "status": "ok",
  "service": "mission-knowledge-assistant"
}
```

---

### `POST /documents`

Cria um documento e gera automaticamente seus chunks.

Exemplo:

```json
{
  "title": "Artemis Mission Overview",
  "content": "Artemis is a NASA program focused on returning humans to the Moon."
}
```

---

### `GET /documents`

Lista os documentos persistidos.

---

### `GET /documents/{id}/chunks`

Lista os chunks associados a um documento.

---

### `GET /search?q=texto`

Executa recuperação textual simples.

A implementação atual utiliza:

```text
ILIKE("%query%")
```

Essa estratégia é intencionalmente simples.

Ela é útil para correspondências literais, nomes, códigos, siglas e identificadores, mas não representa um mecanismo lexical avançado como BM25 ou PostgreSQL Full-Text Search.

---

### `GET /search/semantic`

Executa recuperação semântica usando embeddings e pgvector.

Exemplo:

```text
GET /search/semantic?q=How+does+NASA+plan+to+send+people+back+to+the+Moon&top_k=5
```

A consulta é transformada em embedding usando o mesmo modelo aplicado aos chunks.

O PostgreSQL calcula a distância vetorial e ordena os candidatos.

Conceitualmente:

```sql
ORDER BY embedding <=> :query_embedding
```

Quanto menor a distância de cosseno, maior a proximidade semântica.

---

### `max_distance`

A busca semântica também aceita um limite opcional:

```text
max_distance
```

Exemplo:

```text
GET /search/semantic?q=...&top_k=5&max_distance=0.60
```

Os parâmetros possuem responsabilidades diferentes:

```text
top_k
→ quantidade máxima de candidatos retornados

max_distance
→ fronteira operacional de aceitação
```

Isso permite que a API retorne uma lista vazia quando nenhum resultado estiver suficientemente próximo.

O valor não representa probabilidade e precisa ser calibrado de acordo com modelo, corpus e domínio.

---

### `GET /search/hybrid`

Combina recuperação textual e semântica.

Exemplo:

```text
GET /search/hybrid?q=...&top_k=5&max_distance=0.60&rrf_k=60
```

A estratégia utiliza **Reciprocal Rank Fusion (RRF)**.

Em vez de somar diretamente scores lexicais e distâncias vetoriais com escalas diferentes, o RRF combina as posições dos documentos nos rankings.

Conceitualmente:

```text
RRF score =
Σ 1 / (rrf_k + rank)
```

A implementação mantém os dois retrievers independentes e realiza a fusão posteriormente.

---

## Avaliação de retrieval

Durante a Semana 4 foi criado um experimento controlado para comparar:

```text
busca textual
vs.
busca semântica
```

O corpus utilizado continha cinco documentos e seis consultas representando:

- correspondência literal;
- paráfrase;
- identificador;
- intenção;
- consulta com identificador e linguagem diferente;
- consulta sem resposta relevante no corpus.

### Observações

A recuperação textual foi especialmente previsível para:

```text
termos exatos
identificadores
```

A recuperação semântica foi capaz de encontrar:

```text
paráfrases
intenção
vocabulário diferente
```

Sem um threshold, entretanto, a busca vetorial ainda consegue ordenar candidatos mesmo quando todos são irrelevantes.

---

## Experimento com `max_distance`

No corpus controlado:

| `max_distance` | Casos aprovados | Falsos negativos |
|---|---:|---:|
| `0.40` | 4/6 | 2 |
| `0.60` | 6/6 | 0 |
| `0.80` | 6/6 | 0 |

`0.60` apresentou o melhor equilíbrio **neste pequeno corpus controlado**.

Isso não significa que `0.60` seja um threshold universal.

Com `0.80`, apesar de todos os casos esperados continuarem sendo encontrados, já foi observado candidato adicional menos relevante em uma das consultas.

---

## Experimento com `top_k`

Foram comparados:

```text
top_k = 1
top_k = 3
top_k = 5
```

Nos cinco casos com documento esperado, o resultado correto permaneceu em primeira posição nas três configurações.

Entretanto, o número total de candidatos aumentou:

| `top_k` | Resultados totais | Resultados extras |
|---|---:|---:|
| `1` | 6 | 1 |
| `3` | 18 | 13 |
| `5` | 30 | 25 |

Neste corpus, aumentar `top_k` ampliou principalmente o volume de candidatos.

Esse resultado também não deve ser generalizado: em bases com múltiplos chunks relevantes, valores maiores podem aumentar recall.

---

## Testes

A suíte automatizada utiliza Pytest.

Para executar:

```powershell
pytest
```

Estado atual:

```text
54 passed
```

Os testes cobrem diferentes camadas, incluindo:

- API;
- documentos;
- chunking;
- busca textual;
- embeddings;
- busca semântica;
- threshold;
- Reciprocal Rank Fusion;
- serviço de busca híbrida;
- contrato HTTP da busca híbrida.

Também existem scripts de validação end-to-end para testar integrações reais entre:

```text
modelo de embeddings
PostgreSQL
pgvector
serviços
FastAPI
```

---

## Como rodar localmente

### 1. Criar e ativar o ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Subir o PostgreSQL

```powershell
docker compose up -d
```

### 3. Aplicar migrations

```powershell
alembic upgrade head
```

### 4. Rodar a API

```powershell
uvicorn app.main:app --reload
```

### 5. Abrir a documentação interativa

```text
http://127.0.0.1:8000/docs
```

---

## Estrutura principal

```text
app/
  main.py
  config.py
  database.py
  models.py
  schemas.py
  chunker.py

  routes/
    health.py
    documents.py
    search.py

  services/
    embedding_service.py
    semantic_search.py
    hybrid_search.py
    rank_fusion.py

alembic/
  versions/

docs/
  adr/
  checkins/
  week-04-day-06-search-comparison.md
  week-04-day-07-hybrid-search.md
  diario-tecnico.md

scripts/
  test_embeddings.py
  backfill_embeddings.py
  search_comparison_cases.py
  run_search_comparison.py
  day_07_hybrid_search.py

tests/
```

---

## Decisões arquiteturais

Decisões relevantes são registradas em Architecture Decision Records.

Atualmente existem ADRs para:

- uso do FastAPI;
- persistência com PostgreSQL;
- separação da tabela de chunks;
- estratégia de chunking;
- busca textual com `ILIKE`;
- modelo local de embeddings.

Novas decisões relacionadas à recuperação vetorial e híbrida serão registradas durante o fechamento da Semana 4.

---

## Roadmap

### Semana 1 — API e fundamentos

FastAPI, estrutura modular, configuração, testes e Docker.

### Semana 2 — Persistência

PostgreSQL, SQLModel, Alembic e relacionamento com banco real.

### Semana 3 — Documentos e recuperação textual

Chunking, relação `Document -> Chunk` e busca com `ILIKE`.

### Semana 4 — Retrieval semântico e híbrido ✅

- embeddings;
- pgvector;
- persistência vetorial;
- busca semântica;
- threshold de relevância;
- avaliação controlada;
- comparação textual vs. vetorial;
- busca híbrida com RRF.

### Semana 5 — RAG

Próxima etapa planejada.

A arquitetura de geração ainda será definida após o fechamento técnico e a análise de mercado da Semana 4.

### Etapas posteriores

- avaliação de respostas;
- guardrails e segurança;
- observabilidade;
- análise de custo e latência;
- evolução da recuperação;
- documentação final.

---

## Escopo atual

O Mission Knowledge Assistant **ainda não é um sistema RAG completo**.

O estado atual implementa a camada de backend e retrieval necessária para que essa evolução aconteça de forma controlada.

Atualmente o projeto demonstra:

```text
API REST
+
PostgreSQL
+
modelagem de dados
+
migrations
+
chunking
+
testes
+
embeddings
+
pgvector
+
busca semântica
+
avaliação de retrieval
+
busca híbrida
```

A próxima evolução será integrar uma camada de geração com LLM sem remover a separação entre recuperação, avaliação e geração.