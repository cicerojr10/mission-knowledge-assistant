# Mission Knowledge Assistant

Projeto de portfólio técnico para a trilha de **Engenheiro de Aplicações de IA (LLM)**.

O objetivo é construir, de forma incremental, uma aplicação backend preparada para evoluir em direção a sistemas com documentos, chunking, embeddings, busca vetorial, RAG, avaliação, segurança e preocupações de produção.

## Status atual

O projeto concluiu a **Semana 3** da trilha de desenvolvimento.

Funcionalidades implementadas até o momento:

* API HTTP com FastAPI
* Estrutura modular de rotas
* Persistência com PostgreSQL
* Modelagem com SQLModel
* Controle de schema com Alembic
* Execução local com Docker Compose
* Cadastro e listagem de documentos
* Geração automática de chunks ao criar documentos
* Relacionamento `Document -> Chunk`
* Remoção em cascata entre documentos e chunks
* Endpoint para listar chunks de um documento
* Busca textual simples com `ILIKE`
* Testes automatizados com Pytest
* Registro de decisões arquiteturais em ADRs

Estado atual dos testes:

```text
23 passed
```

## Stack

* Python
* FastAPI
* SQLModel
* PostgreSQL
* Alembic
* Docker
* Pytest

## Objetivo técnico

O projeto simula a construção progressiva de um backend para um assistente de conhecimento baseado em documentos.

A aplicação começa com fundamentos de API e persistência, evolui para chunking e busca textual, e será expandida nas próximas semanas com embeddings, pgvector, busca vetorial e RAG.

## Como rodar localmente

### 1. Criar e ativar o ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Subir o PostgreSQL com Docker Compose

```powershell
docker compose up -d
```

### 3. Aplicar as migrations

```powershell
alembic upgrade head
```

### 4. Rodar a API

```powershell
uvicorn app.main:app --reload
```

### 5. Acessar a documentação interativa

```text
http://127.0.0.1:8000/docs
```

## Endpoints

### GET /health

Verifica se a API está disponível.

Exemplo de resposta:

```json
{
  "status": "ok",
  "service": "mission-knowledge-assistant"
}
```

### POST /documents

Cria um documento e gera automaticamente seus chunks.

Exemplo de request:

```json
{
  "title": "Artemis Mission Overview",
  "content": "Artemis is a NASA program focused on returning humans to the Moon."
}
```

Exemplo de resposta:

```json
{
  "id": 1,
  "title": "Artemis Mission Overview",
  "content": "Artemis is a NASA program focused on returning humans to the Moon.",
  "chunk_count": 1
}
```

### GET /documents

Lista os documentos cadastrados.

### GET /documents/{id}/chunks

Lista os chunks associados a um documento específico.

### GET /search?q=texto

Realiza busca textual simples nos chunks persistidos.

A busca atual utiliza `ILIKE`, uma escolha intencional para manter a Semana 3 focada em fundamentos de persistência, modelagem e recuperação textual simples.

Busca vetorial, embeddings e pgvector serão tratados na Semana 4.

## Chunking

A estratégia atual divide documentos em chunks de tamanho fixo, com sobreposição entre trechos.

Configuração definida na Semana 3:

```text
chunk_size = 500
overlap = 50
```

Essa abordagem foi escolhida por ser simples, previsível e suficiente para preparar o projeto para a próxima etapa: embeddings e busca vetorial.

## Decisões arquiteturais

As principais decisões técnicas são documentadas em ADRs na pasta `docs/adr/`.

ADRs existentes:

* ADR-001 — FastAPI
* ADR-002 — Persistência com PostgreSQL
* ADR-003 — Tabela separada para chunks
* ADR-004 — Estratégia de chunking
* ADR-005 — Busca textual com ILIKE

## Testes

Para executar a suíte de testes:

```powershell
pytest
```

Resultado esperado no estado atual do projeto:

```text
23 passed
```

## Estrutura do projeto

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

alembic/
  versions/

docs/
  adr/
    ADR-000-template.md
    ADR-001-fastapi.md
    ADR-002-postgresql.md
    ADR-003-chunk-table.md
    ADR-004-chunking-strategy.md
    ADR-005-text-search-ilike.md
  checkins/
    semana-01-checkin.md
    semana-02-checkin.md
    semana-03-checkin.md
  semana-01-guia.md
  semana-02-guia.md
  semana-03-guia.md

tests/
  test_health.py
  test_documents.py
  test_chunker.py
  test_search.py
```

## Roadmap

* Semana 1: FastAPI, estrutura do projeto, endpoints, testes e Docker inicial.
* Semana 2: PostgreSQL, Docker Compose, SQLModel, Alembic e persistência.
* Semana 3: Chunking, relação `Document -> Chunk`, busca textual e ADRs.
* Semana 4: Embeddings, pgvector e busca vetorial.
* Semana 5: RAG com LLM.
* Semana 6: Avaliação de respostas.
* Semana 7: Guardrails e segurança.
* Semana 8: Custo, latência, cache e documentação final.

## Escopo atual

Este projeto ainda está em desenvolvimento incremental.

Até a Semana 3, o foco está em backend, persistência, chunking e busca textual. Funcionalidades com LLM, embeddings e RAG ainda não fazem parte do estado atual do projeto.
