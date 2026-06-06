# Mission Knowledge Assistant

Projeto de estudo e portfólio para a trilha de Engenheiro de Aplicações de IA — LLM.

## Objetivo

Construir, passo a passo, uma aplicação de IA aplicada com foco em:

- APIs
- LLMs
- RAG
- embeddings
- guardrails
- evals
- segurança
- observabilidade
- custo e latência

## Dia 1

Criação da API mínima com FastAPI e endpoint de saúde.

## Como rodar localmente

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload