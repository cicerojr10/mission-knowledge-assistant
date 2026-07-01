@'
# Mission Knowledge Assistant

Projeto de estudo e portfólio para a trilha de **Engenheiro de Aplicações de IA (LLM)**.

A aplicação evolui de uma API base em FastAPI para um assistente de conhecimento com persistência, chunking, busca textual, embeddings, busca vetorial e RAG.

## Objetivo

Construir, passo a passo, uma aplicação de IA aplicada com foco em:

- API HTTP com FastAPI
- Persistência em PostgreSQL
- Modelagem de documentos e chunks
- Migrations com Alembic
- Testes automatizados
- Busca textual
- Preparação para embeddings, pgvector e RAG
- Documentação técnica com ADRs

## Estado atual

Até a Semana 3, o projeto possui:

- API FastAPI
- Endpoint de health check
- Cadastro e listagem de documentos
- Persistência em PostgreSQL
- Migrations com Alembic
- Modelagem `Document 1:N Chunk`
- Função de chunking textual com overlap
- Geração automática de chunks ao criar documentos
- Endpoint para listar chunks de um documento
- Endpoint de busca textual com `ILIKE`
- Testes automatizados com pytest

## Stack

- Python
- FastAPI
- Pydantic
- SQLModel
- PostgreSQL
- Alembic
- pytest
- Docker
- Docker Compose

## Como rodar localmente

### 1. Criar ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt