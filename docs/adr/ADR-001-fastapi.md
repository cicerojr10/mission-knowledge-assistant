# ADR-001 - Uso do FastAPI como base da API

## Status

Aceita

## Contexto

O projeto precisa de uma API HTTP simples, clara e evolutiva para servir como base de um assistente de conhecimento baseado em documentos.

Antes de implementar funcionalidades como embeddings, busca vetorial, RAG e avaliação de respostas, é necessário estabelecer uma fundação backend capaz de receber requisições, validar dados, expor endpoints documentados e permitir evolução incremental da aplicação.

## Decisão

Usar FastAPI como framework inicial da API.

## Motivos

* Possui boa integração com type hints do Python.
* Facilita a validação de dados com schemas baseados em Pydantic.
* Gera documentação interativa automaticamente em `/docs`.
* Permite uma estrutura simples para os primeiros endpoints sem impedir crescimento posterior.
* É adequado para aplicações backend que podem evoluir para fluxos envolvendo documentos, busca, embeddings e LLMs.

## Trade-offs

* Em ambientes corporativos orientados a Java, Spring Boot pode ser uma escolha mais comum.
* Para APIs muito pequenas, Flask poderia ser suficiente.
* FastAPI exige familiaridade com type hints, schemas, validação de dados e organização modular da aplicação.

## Consequências

O projeto passa a ter uma base backend em Python, com documentação automática, validação estruturada e uma arquitetura adequada para evolução incremental.

Essa decisão mantém o projeto alinhado à trilha de Engenharia de Aplicações de IA, permitindo integração futura com persistência, chunking, embeddings, bancos vetoriais e LLMs.
