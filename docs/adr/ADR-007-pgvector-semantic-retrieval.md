# ADR-007 - pgvector para recuperação semântica

## Status

Aceita

## Contexto

O Mission Knowledge Assistant já utiliza PostgreSQL para persistir documentos e chunks.

Na Semana 4, o projeto passou a gerar embeddings com o modelo `sentence-transformers/all-MiniLM-L6-v2`, com 384 dimensões.

Era necessário persistir esses vetores e permitir recuperação semântica sem introduzir uma segunda infraestrutura de armazenamento antes de existir necessidade comprovada.

## Decisão

Utilizar a extensão `pgvector` no PostgreSQL existente.

Os embeddings são associados aos chunks e armazenados como `vector(384)`.

A consulta do usuário é convertida em embedding com o mesmo modelo usado nos chunks.

A busca semântica utiliza distância de cosseno.

Conceitualmente, a consulta ordena os chunks pela distância vetorial entre o embedding persistido e o embedding da query.

Quanto menor a distância, maior a proximidade semântica segundo o modelo.

A busca textual com `ILIKE` continuará disponível separadamente.

## Motivos

- reutilizar o PostgreSQL já presente no projeto;
- manter dados relacionais e vetoriais na mesma infraestrutura;
- evitar complexidade operacional prematura;
- manter relação direta entre `Chunk` e embedding;
- permitir estudo explícito de persistência e retrieval vetorial;
- deixar otimizações de escala para quando houver evidência de necessidade.

## Ranking e aceitação

`top_k` controla a quantidade máxima de candidatos retornados.

Ele não garante relevância.

Por isso a busca semântica também possui o parâmetro opcional `max_distance`.

`top_k` controla quantidade.

`max_distance` controla aceitação.

Uma lista vazia é uma resposta válida quando nenhum candidato satisfaz o limite.

O valor de `max_distance` não deve ser tratado como universal. Ele depende do modelo, corpus, domínio e tipo de consulta.

## Alternativas consideradas

### Banco vetorial separado

Adiado.

Soluções especializadas podem ser úteis em outros cenários, mas adicionariam outra infraestrutura antes de o projeto demonstrar essa necessidade.

### Manter apenas busca textual

Rejeitado porque correspondência literal não resolve adequadamente consultas por significado.

### Adicionar HNSW ou IVFFlat imediatamente

Adiado.

Ainda não existe medição indicando gargalo de escala que justifique busca aproximada.

## Consequências

O projeto passa a suportar recuperação textual e semântica como mecanismos independentes.

Embeddings continuam sendo dados derivados. Uma troca futura de modelo pode exigir regeneração dos vetores e, dependendo da dimensão, alteração de schema.

A decisão prepara a camada de retrieval para uma futura arquitetura RAG, mas não significa que RAG já esteja implementado.

## Validação

Foram validados:

- embeddings persistidos com 384 dimensões;
- backfill de chunks pendentes;
- busca semântica end-to-end;
- `top_k`;
- `max_distance`;
- retorno vazio quando nenhum candidato é aceito.

A avaliação controlada está documentada em `docs/week-04-day-06-search-comparison.md`.

Os resultados são evidência do corpus utilizado e não um benchmark de produção.
