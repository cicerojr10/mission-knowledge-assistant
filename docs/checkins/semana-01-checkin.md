# Check-in — Semana 1

## Objetivo da semana

Construir a base profissional do projeto Mission Knowledge Assistant, preparando o caminho para uma aplicação de IA com LLMs, RAG, embeddings, guardrails e evals.

---

## Dia 1 — API mínima com FastAPI

- [x] Criar estrutura inicial do projeto
- [x] Criar ambiente virtual Python
- [x] Instalar FastAPI e Uvicorn
- [x] Criar endpoint `GET /health`
- [x] Rodar API localmente
- [x] Testar `/health`
- [x] Testar `/docs`
- [x] Criar README inicial
- [x] Enviar para o GitHub

### Aprendizado principal

Entendi que uma API é um contrato entre sistemas e que `/health` é usado para verificar se a aplicação está viva.

---

## Dia 2 — Estrutura profissional do projeto

- [x] Criar ou revisar `app/config.py`
- [x] Criar ou revisar `app/schemas.py`
- [x] Separar rota de health em `app/routes/health.py`
- [x] Manter `main.py` mais limpo
- [x] Testar `/health`
- [x] Testar `/docs`
- [x] Atualizar README
- [x] Fazer commit

### Aprendizado principal

Entendi a importância de separar responsabilidades no projeto para facilitar manutenção e evolução.

---

## Dia 3 — GitHub como diário de engenharia

- [x] Criar pasta `docs/`
- [x] Criar `docs/diario-tecnico.md`
- [x] Criar `docs/checkins/semana-01-checkin.md`
- [x] Criar pasta `docs/adr/`
- [x] Criar template de ADR
- [x] Atualizar README
- [ ] Fazer commit
- [ ] Enviar para o GitHub

### Aprendizado principal

Ainda vou preencher ao final do dia.

---

## Dia 4 — Endpoint de documentos

- [ ] Criar schema `DocumentCreate`
- [ ] Criar schema `DocumentResponse`
- [ ] Criar `POST /documents`
- [ ] Criar `GET /documents`
- [ ] Testar no `/docs`

---

## Dia 5 — Configuração, logs e erros

- [ ] Criar `.env.example`
- [ ] Melhorar configurações
- [ ] Tratar erros básicos
- [ ] Padronizar mensagens

---

## Dia 6 — Testes automatizados

- [ ] Instalar pytest
- [ ] Criar teste para `/health`
- [ ] Criar teste para `/documents`
- [ ] Rodar testes

---

## Dia 7 — Docker e revisão

- [ ] Criar Dockerfile
- [ ] Criar `.dockerignore`
- [ ] Rodar aplicação com Docker
- [ ] Criar ADR-001
- [ ] Revisar README