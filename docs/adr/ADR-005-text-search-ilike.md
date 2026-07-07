# ADR-005 - Busca textual inicial com ILIKE

## Status

Aceita

## Contexto

A aplicação passou a persistir documentos e chunks em PostgreSQL.

Com os chunks disponíveis, a Semana 3 precisa adicionar uma primeira forma de recuperação de informação antes da introdução de embeddings, pgvector e RAG.

O objetivo desta etapa é permitir busca textual simples sobre os chunks persistidos, validando o fluxo básico de recuperação de trechos a partir de uma consulta.

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
```

## Motivos

* `ILIKE` permite busca textual case-insensitive de forma simples.
* A abordagem é suficiente para validar a recuperação inicial de chunks.
* Evita introduzir complexidade prematura antes da Semana 4.
* Mantém o foco da Semana 3 em persistência, chunking, relacionamento entre tabelas e recuperação textual básica.
* Permite testar o fluxo de busca sem depender ainda de embeddings, pgvector ou LLMs.
* Cria uma base comparável para evoluções futuras, como Full Text Search e busca vetorial.

## Alternativas consideradas

### Usar PostgreSQL Full Text Search

Adiada porque adicionaria complexidade extra de indexação, ranking e configuração linguística. Essa alternativa pode ser considerada futuramente caso a busca textual simples se torne insuficiente.

### Usar embeddings com pgvector

Rejeitada neste momento porque embeddings e busca vetorial pertencem ao escopo da Semana 4.

### Buscar diretamente em documentos completos

Rejeitada porque a Semana 3 já definiu chunks como unidade principal de recuperação. Buscar em documentos completos reduziria a granularidade dos resultados.

### Usar LLM para interpretar consultas

Rejeitada porque RAG e integração com LLM ainda não fazem parte do escopo atual do projeto.

## Trade-offs

A busca com `ILIKE` é simples e fácil de implementar, mas possui limitações importantes.

Ela não oferece ranking semântico, não entende intenção da consulta e pode ter desempenho limitado em bases maiores se não houver estratégia adequada de indexação.

Também depende de correspondência literal ou parcial de texto, o que significa que termos semanticamente próximos podem não ser encontrados.

Apesar dessas limitações, a abordagem é adequada para o estágio atual do projeto, pois valida a recuperação de chunks persistidos antes da introdução de mecanismos mais avançados.

## Consequências

O projeto passa a ter um primeiro endpoint de recuperação de informação.

A unidade de busca passa a ser o chunk, não o documento completo.

A API consegue retornar trechos relacionados a uma consulta textual simples.

A decisão mantém a Semana 3 focada em fundamentos de backend e persistência, preparando a transição para embeddings, pgvector e busca vetorial na Semana 4.
