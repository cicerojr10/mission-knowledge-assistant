# ADR-001 — Usar FastAPI como base da API

## Status

Aceita

## Contexto

O projeto Mission Knowledge Assistant precisa de uma API para receber requisições, expor endpoints e servir como base para funcionalidades futuras de IA aplicada, como ingestão de documentos, busca semântica, RAG, evals e guardrails.

Antes de implementar componentes de IA, é necessário ter uma base backend simples, clara e evolutiva.

## Decisão

Usar FastAPI como framework principal da API.

## Motivos

- É uma ferramenta moderna para construção de APIs em Python.
- Combina bem com projetos de IA, dados e automação.
- Possui documentação automática em `/docs`.
- Usa type hints e Pydantic para validação de dados.
- Permite evoluir o projeto de forma organizada.

## Alternativas consideradas

### Flask

Seria uma opção mais simples, mas exigiria mais configuração manual para documentação e validação.

### Django

É uma opção robusta, mas mais pesada para este momento do projeto.

### Spring Boot com Java

É forte no mercado corporativo, mas meu foco atual está em aplicações de IA com Python, LLMs, RAG e evals.

## Trade-offs

### Ganhos

- Desenvolvimento rápido.
- Boa integração com ecossistema Python.
- Documentação automática.
- Boa base para APIs de IA aplicada.

### Perdas

- Em algumas empresas Java, Spring Boot pode ser mais comum.
- Exige cuidado para manter boa organização conforme o projeto cresce.

## Consequências

A escolha do FastAPI facilita a evolução para funcionalidades como:

- ingestão de documentos;
- endpoints de busca;
- integração com LLMs;
- criação de evals;
- APIs para RAG;
- validação de entradas e saídas.