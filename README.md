# Mission Knowledge Assistant

Projeto de estudo e portfolio para a trilha de **Engenheiro de Aplicacoes de IA (LLM)**.

## Objetivo

Construir, passo a passo, uma aplicacao de IA aplicada baseada em API, documentos, RAG, embeddings, guardrails, evals, seguranca e preocupacao com producao.

Na Semana 1, o foco e a base profissional:

- FastAPI
- rotas HTTP
- estrutura de projeto
- GitHub como diario de engenharia
- endpoint de documentos em memoria
- logs
- tratamento de erro
- testes automatizados
- Docker inicial
- ADRs

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

Verifica se a API esta viva.

Exemplo de resposta:

```json
{
  "status": "ok",
  "service": "mission-knowledge-assistant"
}
```

### POST /documents

Cadastra um documento em memoria.

Exemplo de request:

```json
{
  "title": "Artemis Mission Overview",
  "content": "Artemis is a NASA program focused on returning humans to the Moon."
}
```

### GET /documents

Lista documentos cadastrados em memoria.

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
  semana-01-guia.md
  diario-tecnico-template.md
  adr/
    ADR-000-template.md
    ADR-001-fastapi.md
  checkins/
    semana-01-checkin.md
```

## Diario tecnico

Use a pasta `docs/` para registrar aprendizado diario. O objetivo nao e apenas salvar codigo, mas criar evidencia do seu raciocinio tecnico.

## Configuração

O projeto usa variáveis de ambiente para permitir configurações diferentes entre ambiente local, desenvolvimento e produção.

Exemplo disponível em:

```text
.env.example

## Proximas semanas

- Semana 2: PostgreSQL, Docker Compose, persistencia e inicio de modelagem.
- Semana 3: chunking e ingestao de documentos.
- Semana 4: embeddings, pgvector e busca vetorial.
- Semana 5: RAG com LLM.
- Semana 6: evals.
- Semana 7: guardrails e seguranca.
- Semana 8: custo, latencia, cache e documentacao final.