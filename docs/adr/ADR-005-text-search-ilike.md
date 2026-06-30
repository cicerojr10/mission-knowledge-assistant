# ADR-005 - Busca textual inicial com ILIKE

## Status

Aceita

## Contexto

A aplicação passou a persistir documentos e chunks em PostgreSQL.

Com os chunks disponíveis, a Semana 3 precisa adicionar uma primeira forma de recuperação de informação antes da introdução de embeddings, pgvector e RAG.

O objetivo desta etapa é permitir busca textual simples sobre os chunks persistidos.

## Decisão

Implementar o endpoint `GET /search?q=termo` usando busca textual com `ILIKE` sobre o campo `chunks.content`.

A busca retorna os chunks encontrados junto com dados mínimos do documento de origem.

A resposta inclui:

```text
chunk_id
document_id
document_title
content
chunk_index
char_count