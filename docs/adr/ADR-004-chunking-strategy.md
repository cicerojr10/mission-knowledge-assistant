# ADR-004 - Estratégia inicial de chunking

## Status

Aceita

## Contexto

A aplicação passou a modelar chunks em tabela separada, relacionados a documentos.

Para que essa estrutura seja útil, é necessário definir uma estratégia inicial para quebrar o texto completo de um documento em trechos menores.

A Semana 3 ainda não usa embeddings nem pgvector. O objetivo atual é preparar a base para busca textual e, posteriormente, busca semântica.

## Decisão

Implementar uma função de chunking em `app/chunker.py` chamada `split_text`.

A função divide texto por tamanho fixo de caracteres, usando os valores iniciais:

```text
chunk_size = 500
overlap = 50