# ADR-003 - Modelar chunks em tabela separada

## Status

Aceita

## Contexto

O projeto passou a persistir documentos em PostgreSQL. Até este momento, cada documento era tratado como um bloco único de texto.

Para evoluir a aplicação em direção a busca textual, embeddings e RAG, é necessário quebrar documentos em trechos menores chamados chunks.

Chunks precisam ser persistidos, ordenados e associados ao documento original. Essa estrutura deve permitir consultar trechos específicos sem depender de carregar o documento completo.

## Decisão

Criar uma tabela separada chamada `chunks`.

Cada chunk será associado a um documento por meio de uma foreign key `document_id`.

A relação será modelada como:

```text
Document 1:N Chunk