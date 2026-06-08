# Mission Knowledge Assistant

Projeto de estudo e portfólio para a trilha de **Engenheiro de Aplicações de IA (LLM)**.

## Objetivo

Construir, passo a passo, uma aplicação de IA aplicada baseada em API, documentos, RAG, embeddings, guardrails, evals, segurança e preocupação com produção.

Este projeto funciona como laboratório prático para aprender a transformar IA generativa em uma aplicação real, com backend, documentação, testes, decisões técnicas e evolução incremental.

## Foco da Semana 1

Na Semana 1, o foco é criar a base profissional do projeto:

* FastAPI
* rotas HTTP
* estrutura de projeto
* GitHub como diário de engenharia
* endpoint de documentos em memória
* logs
* tratamento de erro
* testes automatizados
* Docker inicial
* ADRs

## Como rodar localmente

### 1. Criar ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Rodar a API

```powershell
uvicorn app.main:app --reload
```

### 3. Acessar

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## Endpoints da Semana 1

### GET /health

Verifica se a API está viva.

Exemplo de resposta:

```json
{
  "status": "ok",
  "service": "mission-knowledge-assistant"
}
```

### POST /documents

Cadastra um documento em memória.

Exemplo de request:

```json
{
  "title": "Artemis Mission Overview",
  "content": "Artemis is a NASA program focused on returning humans to the Moon."
}
```

### GET /documents

Lista documentos cadastrados em memória.

## Rodar testes

```powershell
pytest
```

## Rodar com Docker

```powershell
docker build -t mission-knowledge-assistant .
docker run -p 8000:8000 mission-knowledge-assistant
```

## Estrutura do projeto

```text
app/
  main.py
  config.py
  schemas.py
  routes/
    health.py
    documents.py
tests/
  test_health.py
  test_documents.py
docs/
  diario-tecnico.md
  semana-01-guia.md
  diario-tecnico-template.md
  adr/
    ADR-000-template.md
    ADR-001-fastapi.md
  checkins/
    semana-01-checkin.md
```

## Diário de engenharia

Este projeto também funciona como um registro público de aprendizado técnico.

A pasta `docs/` contém materiais que mostram a evolução do projeto:

* `docs/diario-tecnico.md`: registro dos aprendizados diários.
* `docs/checkins/semana-01-checkin.md`: checklist de progresso da semana.
* `docs/adr/`: decisões arquiteturais registradas.

## Por que isso importa?

Além de construir código, este projeto documenta decisões técnicas, erros, aprendizados e a relação entre cada etapa do projeto e o dia a dia real de trabalho.

Essa prática ajuda a desenvolver raciocínio de engenharia, clareza de comunicação e capacidade de manutenção de projetos.

## Próximas semanas

* Semana 2: PostgreSQL, Docker Compose, persistência e início de modelagem.
* Semana 3: chunking e ingestão de documentos.
* Semana 4: embeddings, pgvector e busca vetorial.
* Semana 5: RAG com LLM.
* Semana 6: evals.
* Semana 7: guardrails e segurança.
* Semana 8: custo, latência, cache e documentação final.
