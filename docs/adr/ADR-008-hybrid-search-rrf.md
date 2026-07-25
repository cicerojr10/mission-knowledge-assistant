# ADR-008 - Busca híbrida com Reciprocal Rank Fusion

## Status

Aceita

## Contexto

Ao final da Semana 4, o Mission Knowledge Assistant possuía dois mecanismos independentes de recuperação:

- busca textual com `ILIKE`;
- busca semântica com embeddings e pgvector.

Os experimentos mostraram características complementares.

A busca textual é previsível para correspondências literais, identificadores, siglas e termos exatos.

A busca semântica consegue recuperar conteúdo relacionado mesmo quando a consulta utiliza palavras diferentes.

Era necessário combinar esses dois rankings sem tratar sinais diferentes como se fossem diretamente comparáveis.

## Decisão

Implementar uma busca híbrida utilizando Reciprocal Rank Fusion (RRF).

O fluxo é:

query
→ retrieval textual
→ ranking textual

query
→ retrieval semântico
→ ranking semântico

rankings
→ RRF
→ ranking híbrido

O RRF utiliza principalmente a posição de cada item nos rankings.

Conceitualmente, cada ocorrência contribui com:

`1 / (rrf_k + rank)`

O valor padrão atual de `rrf_k` é 60.

## Motivos

- evitar soma direta de sinais com escalas diferentes;
- preservar os retrievers existentes;
- manter baixo acoplamento entre textual e semântico;
- permitir testes separados de cada estratégia;
- manter implementação simples e determinística;
- evitar introduzir um modelo adicional de reranking nesta etapa.

## Por que não somar scores diretamente

A busca semântica utiliza distância de cosseno, em que valores menores representam maior proximidade.

A busca textual atual utiliza `ILIKE` e não possui um score lexical contínuo equivalente.

Somar diretamente esses valores não teria uma interpretação técnica defensável sem uma etapa explícita de normalização e calibração.

O RRF evita esse problema usando a posição dos candidatos.

## Retrievers independentes

Os endpoints continuam separados:

- `GET /search`
- `GET /search/semantic`
- `GET /search/hybrid`

Essa separação permite comparar estratégias e investigar regressões sem depender da camada híbrida.

Quando `max_distance` é utilizado, ele continua sendo aplicado no retrieval semântico antes da fusão.

## Comportamento

Um candidato presente nos dois rankings recebe contribuição dos dois lados.

Um candidato presente em apenas um ranking ainda pode participar do resultado híbrido.

A implementação considera a primeira ocorrência de cada item em cada ranking e utiliza critérios determinísticos de desempate.

O objetivo é manter resultados reproduzíveis para as mesmas entradas.

## Alternativas consideradas

### Somar diretamente scores

Rejeitado nesta etapa porque os sinais não possuem escalas diretamente comparáveis.

### Normalizar scores manualmente

Adiado.

Isso adicionaria novas hipóteses e parâmetros antes de existir evidência suficiente para justificar a complexidade.

### Utilizar somente busca semântica

Rejeitado porque correspondência literal e identificadores continuam sendo casos relevantes.

### Adicionar um reranker com outro modelo

Adiado.

Um cross-encoder ou outro reranker adicionaria custo, latência e uma nova etapa de inferência antes de ser necessária.

## Trade-offs

O RRF simplifica a combinação de rankings, mas não utiliza toda a informação presente na magnitude dos scores originais.

Ele também não corrige um retriever ruim.

RRF combina rankings; ele não cria relevância inexistente.

A qualidade final continua dependendo dos mecanismos de recuperação que alimentam a fusão.

## Consequências

O projeto passa a oferecer três estratégias explícitas:

- textual;
- semântica;
- híbrida.

Isso cria uma base para experimentos posteriores antes da camada de geração.

Retrieval e generation continuam sendo responsabilidades diferentes.

A existência de busca híbrida não significa que o projeto já possua RAG completo.

## Validação

Foram criados testes específicos para:

- algoritmo de RRF;
- primeira ocorrência;
- validação de `rrf_k`;
- ordenação determinística;
- serviço híbrido;
- contrato HTTP do endpoint híbrido.

Também foi executada uma validação end-to-end com embeddings reais e documentos temporários.

O resultado observado foi:

`hybrid_validation=PASS`

Ao final da implementação, a suíte completa possuía:

`54 passed`

A decisão foi validada funcionalmente e em um cenário controlado, não em um benchmark de produção.
