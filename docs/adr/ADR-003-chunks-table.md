# ADR-003 - Modelagem de chunks em tabela separada

## Status

Aceita

## Contexto

O projeto passou a persistir documentos em PostgreSQL. Até este momento, cada documento era tratado como um bloco único de texto.

Para evoluir a aplicação em direção a busca textual, embeddings, busca vetorial e RAG, é necessário dividir documentos em trechos menores chamados chunks.

Chunks precisam ser persistidos, ordenados e associados ao documento original. Essa estrutura deve permitir consultar trechos específicos sem depender de carregar o documento completo.

## Decisão

Criar uma tabela separada chamada `chunks`.

Cada chunk será associado a um documento por meio de uma foreign key `document_id`.

A relação será modelada como:

```text
Document 1:N Chunk
```

Cada registro de chunk deve armazenar, no mínimo:

* identificador próprio;
* conteúdo textual do chunk;
* posição do chunk dentro do documento;
* referência ao documento original.

## Motivos

* Permite recuperar trechos específicos de um documento.
* Facilita busca textual diretamente sobre chunks.
* Prepara a aplicação para geração futura de embeddings por chunk.
* Evita carregar documentos completos para operações de busca.
* Mantém a relação explícita entre documento original e seus trechos derivados.
* Permite preservar a ordem dos chunks por meio de um campo de posição.

## Alternativas consideradas

### Salvar chunks como array dentro da tabela `document`

Rejeitada porque dificultaria consultas individuais, busca textual, indexação e futura associação de embeddings a cada chunk.

### Manter apenas o documento completo

Rejeitada porque documentos grandes não são adequados para busca granular, embeddings ou recuperação de contexto em pipelines de RAG.

### Criar chunks apenas em memória no momento da busca

Rejeitada porque geraria processamento repetido, dificultaria testes e impediria persistir metadados associados a cada chunk.

## Trade-offs

A tabela separada adiciona complexidade ao modelo de dados, pois passa a existir uma relação entre documentos e chunks.

Também é necessário garantir consistência entre documento e chunks, especialmente em operações de criação, remoção e testes.

Em contrapartida, essa estrutura oferece uma base mais adequada para busca textual, embeddings e recuperação de contexto.

## Consequências

A aplicação passa a ter uma relação `Document -> Chunk`.

A criação de documentos pode gerar registros derivados na tabela `chunks`.

A remoção de documentos precisa considerar os chunks associados.

Testes que manipulam documentos precisam limpar ou considerar também os chunks para evitar estado persistido entre execuções.

Essa decisão prepara o projeto para as próximas etapas da trilha, especialmente busca textual por trechos, embeddings com pgvector e RAG.
