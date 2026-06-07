# ADR-001 - Usar FastAPI como base da API

## Status

Aceita

## Contexto

O projeto precisa de uma API simples, clara e evolutiva para servir como base de uma aplicacao de IA aplicada. Antes de implementar RAG, embeddings e evals, precisamos de um backend que receba requisicoes, valide dados e exponha endpoints documentados.

## Decisao

Usar FastAPI como framework inicial da API.

## Motivos

- E uma ferramenta moderna para APIs em Python.
- Gera documentacao automatica em `/docs`.
- Usa type hints e Pydantic para validacao.
- Combina bem com projetos de IA, dados e automacao.
- Permite evoluir para endpoints de documentos, busca, RAG e evals.

## Trade-offs

- Para empresas Java, Spring Boot pode ser mais comum.
- Para sistemas muito simples, Flask poderia ser suficiente.
- FastAPI exige entender type hints, schemas e validacao.

## Consequencias

O projeto fica alinhado com a trilha de Engenheiro de Aplicacoes de IA, mantendo Python como stack principal e permitindo integracao futura com embeddings, bancos vetoriais e LLMs.
