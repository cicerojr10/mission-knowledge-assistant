# Mission Knowledge Assistant

Backend para um assistente de conhecimento baseado em documentos, desenvolvido de forma incremental com **Python, FastAPI, PostgreSQL e pgvector**.

O projeto começou com fundamentos de API, persistência e recuperação textual e está evoluindo progressivamente para **busca semântica, recuperação híbrida e aplicações de IA/LLM**.

O objetivo não é apenas adicionar tecnologias, mas construir e validar cada camada separadamente antes de avançar para RAG.

---

## Status atual

**Security Slice concluído — RAG em desenvolvimento**

O backend atualmente possui:

- API REST com FastAPI e PostgreSQL;
- modelagem com SQLModel e migrations com Alembic;
- autenticação com JWT e armazenamento seguro de senhas;
- autorização e isolamento de documentos por proprietário;
- criação de documentos e geração de chunks;
- embeddings persistidos com pgvector;
- busca textual, semântica e híbrida com RRF;
- construção de contexto RAG com fontes;
- mecanismo de abstenção;
- adapter OpenAI para avaliação semântica de answerability;
- testes automatizados com banco PostgreSQL isolado.

Última validação local:

```text
180 passed, 1 warning
```

**Limitações atuais:**

O RAG ainda não possui um gerador de respostas LLM funcional
integrado de ponta a ponta.

A integração de avaliação semântica com OpenAI foi validada
com clientes simulados, sem chamadas reais à API.

O projeto é um backend em desenvolvimento e não está
validado para produção.

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

A suíte automatizada utiliza Pytest e PostgreSQL com pgvector.

Última execução local validada:

```text
180 passed, 1 warning
```

A suíte cobre autenticação, autorização, isolamento por proprietário,
documentos, chunks, retrieval textual, semântico e híbrido,
construção de contexto RAG, abstenção e adapters de provedores.

Os testes da integração OpenAI utilizam clientes simulados.
Uma chamada real à API OpenAI ainda não foi validada.

### Banco de testes

Os testes de integração utilizam `mission_knowledge_test`,
separado do banco local da aplicação (`mission_knowledge`).

O arquivo `tests/conftest.py` configura esse destino antes da
coleta dos testes e desabilita as credenciais OpenAI no ambiente
inicial do Pytest.

Os dois bancos ainda compartilham o mesmo usuário PostgreSQL.
Portanto, esse isolamento não substitui permissões independentes
nem representa uma configuração de produção.

### Preparação inicial

Com o PostgreSQL do Docker Compose em execução, crie o banco
de testes uma única vez:

```powershell
docker compose exec -T postgres psql -U mission_user -d postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE mission_knowledge_test OWNER mission_user TEMPLATE template0;"
```

Se o banco já existir, não repita a criação.

Antes de executar a suíte pela primeira vez, aplique as migrations
exclusivamente ao banco de testes:

```powershell
@'
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

config = Config("alembic.ini")
url = make_url(
    config.get_main_option("sqlalchemy.url")
).set(database="mission_knowledge_test")

engine = create_engine(url)

with engine.connect() as connection:
    actual_database = connection.execute(
        text("SELECT current_database()")
    ).scalar_one()

engine.dispose()

if actual_database != "mission_knowledge_test":
    raise RuntimeError(
        f"Unsafe migration target: {actual_database}"
    )

config.set_main_option(
    "sqlalchemy.url",
    url.render_as_string(hide_password=False),
)

command.upgrade(config, "head")
print("Test database migrations applied.")
'@ | python -
```

### Execução

No terminal integrado, com o ambiente virtual ativo:

```powershell
python -m pytest -q
```

Os testes de integração podem criar e excluir registros no banco
`mission_knowledge_test`. Não execute a suíte contra um banco que
contenha dados que precisem ser preservados.

O aviso de depreciação relacionado à constante HTTP 413 é uma
limitação conhecida e não bloqueia a execução atual.

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


### Semana 5 — RAG (em desenvolvimento)

Implementações já realizadas:

- construção de contexto a partir do retrieval autorizado;
- identificação das fontes utilizadas;
- mecanismo de abstenção;
- separação entre avaliação de answerability e geração;
- adapter OpenAI para avaliação semântica;
- tratamento de falhas de provedores externos;
- testes automatizados com clientes simulados.

Pendências:

- integração funcional de um gerador de respostas com LLM;
- validação controlada com a API OpenAI real;
- avaliação da qualidade das respostas e da fundamentação nas fontes;
- medição de custo, latência e comportamento em diferentes cenários.

A implementação atual é incremental e ainda não representa
um sistema RAG completo ou validado para produção.


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

O projeto já implementa a base backend, mecanismos de retrieval
e parte da arquitetura RAG, incluindo construção de contexto,
fontes, abstenção e avaliação semântica com clientes simulados.

A geração funcional com LLM e a validação ponta a ponta ainda
estão pendentes.

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