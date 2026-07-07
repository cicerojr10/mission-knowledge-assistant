# ADR-004 - Estratégia inicial de chunking

## Status

Aceita

## Contexto

A aplicação passou a modelar chunks em tabela separada, relacionados a documentos.

Para que essa estrutura seja útil, é necessário definir uma estratégia inicial para quebrar o texto completo de um documento em trechos menores.

A Semana 3 ainda não usa embeddings nem pgvector. O objetivo atual é preparar a base para busca textual e, posteriormente, busca semântica.

## Decisão

Implementar uma função de chunking em `app/chunker.py` chamada `split_text`.

A função divide o texto por tamanho fixo de caracteres, usando os valores iniciais:

```text id="o35th8"
chunk_size = 500
overlap = 50
```

A função também valida entradas inválidas, como texto vazio, `chunk_size` inválido e `overlap` maior ou igual ao tamanho do chunk.

## Motivos

* A estratégia por tamanho fixo é simples de implementar, testar e revisar.
* `chunk_size = 500` cria trechos pequenos o suficiente para busca e inspeção manual.
* `overlap = 50` reduz o risco de perda de contexto entre chunks consecutivos.
* A abordagem é adequada para a Semana 3, pois o foco atual é consolidar persistência, relação `Document -> Chunk` e busca textual.
* A função isolada em `app/chunker.py` permite evoluir a estratégia no futuro sem acoplar a lógica diretamente às rotas da API.

## Alternativas consideradas

### Não usar overlap

Rejeitada porque a quebra seca entre chunks pode separar informações relacionadas e prejudicar a recuperação de contexto.

### Usar chunks muito pequenos

Rejeitada porque aumentaria o número de registros, geraria mais ruído na busca e poderia fragmentar demais o conteúdo.

### Usar chunks muito grandes

Rejeitada porque reduziria a granularidade da busca e dificultaria a recuperação de trechos específicos.

### Usar chunking semântico desde o início

Rejeitada neste momento para evitar complexidade prematura. A Semana 3 tem como objetivo criar uma base simples e confiável antes de introduzir embeddings e técnicas semânticas.

## Trade-offs

A estratégia por tamanho fixo não entende a estrutura semântica do texto. Ela pode cortar frases, parágrafos ou ideias no meio.

O overlap reduz parte desse problema, mas também gera repetição de conteúdo entre chunks e aumenta o volume de dados armazenados.

Apesar dessas limitações, a abordagem é previsível, fácil de testar e suficiente para preparar o projeto para a próxima etapa.

## Consequências

A criação de documentos pode gerar múltiplos chunks derivados do conteúdo original.

Os chunks passam a ter tamanho previsível e uma ordem definida dentro do documento.

A busca textual passa a operar sobre trechos menores, em vez de documentos completos.

A estratégia poderá ser revista no futuro, especialmente após a introdução de embeddings, pgvector e avaliação de qualidade da recuperação.
