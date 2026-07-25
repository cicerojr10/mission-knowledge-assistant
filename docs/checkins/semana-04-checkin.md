# Check-in — Semana 4

## Tema

Embeddings, pgvector, busca semântica, avaliação de retrieval e busca híbrida.

## Objetivo da semana

Evoluir o Mission Knowledge Assistant da busca textual simples para uma arquitetura capaz de representar e recuperar chunks por significado.

Estado inicial:

Document
→ Chunk
→ PostgreSQL
→ busca textual com ILIKE

Estado alcançado:

Document
→ Chunk
→ Embedding
→ PostgreSQL + pgvector
→ retrieval textual, semântico e híbrido

## Fundamentos e infraestrutura

Foi escolhido o modelo local:

`sentence-transformers/all-MiniLM-L6-v2`

Cada embedding possui:

`384 dimensões`

O PostgreSQL passou a utilizar pgvector e os embeddings dos chunks são persistidos como `vector(384)`.

A decisão de utilizar um modelo local foi registrada no ADR-006.

A decisão de utilizar pgvector para retrieval semântico foi registrada no ADR-007.

## Embeddings persistentes

Foi criado um serviço reutilizável de embeddings com:

- lazy loading;
- cache do modelo;
- geração em lote;
- validação de entrada;
- validação de dimensionalidade.

O texto continua sendo a fonte de verdade.

O embedding é tratado como dado derivado.

Também foi criado um backfill para processar apenas chunks cujo embedding ainda é nulo.

Na validação:

- primeira execução: 2 chunks processados;
- segunda execução: 0 chunks processados;
- dimensão confirmada: 384.

## Busca semântica

Foi implementado:

`GET /search/semantic`

Fluxo:

query
→ embedding
→ comparação vetorial
→ cosine distance
→ ranking
→ top_k

Quanto menor a distância, maior a proximidade semântica segundo o modelo.

Em uma validação end-to-end, a consulta:

`How will NASA send people back to the Moon?`

recuperou primeiro o conteúdo relacionado ao programa Artemis.

Esse resultado demonstrou o funcionamento do pipeline, não qualidade geral de produção.

## Ranking versus aceitação

Durante os testes ficou evidente que um ranking sempre pode apresentar um primeiro colocado mesmo quando todos os candidatos são ruins.

Por isso foi introduzido o parâmetro opcional:

`max_distance`

Responsabilidades:

`top_k` → quantidade de candidatos

`max_distance` → critério operacional de aceitação

Uma lista vazia passou a ser uma resposta válida quando nenhum candidato satisfaz o limite.

## Avaliação controlada

Foi construído um corpus temporário com cinco documentos e seis consultas.

Os casos incluíram:

- correspondência literal;
- paráfrase;
- identificador;
- intenção;
- frase mista;
- consulta sem resposta relevante.

O caso sem resposta foi:

`How do I prepare pizza dough?`

Sem threshold, a busca semântica ainda retornava candidatos irrelevantes.

Isso demonstrou a diferença entre ranking e relevância absoluta.

## Experimento com max_distance

Foram observados:

`0.40` → 4 casos aprovados e 2 falsos negativos

`0.60` → 6 casos aprovados, sem falsos negativos registrados

`0.80` → 6 casos aprovados, mas com ruído adicional observado

No pequeno corpus utilizado, `0.60` apresentou o melhor equilíbrio.

Esse valor não deve ser tratado como threshold universal.

Também foi identificado que o contador simples do experimento não penalizava todo candidato irrelevante adicional em consultas positivas.

Portanto, "0 falsos positivos" não significava necessariamente "0 ruído".

## Experimento com top_k

Foram avaliados:

`top_k = 1`

`top_k = 3`

`top_k = 5`

Nos cinco casos positivos, o documento esperado permaneceu em primeiro lugar.

Ao aumentar `top_k`, aumentou principalmente a quantidade de candidatos extras neste corpus.

Esse comportamento não deve ser generalizado para outros conjuntos de dados.

## Dia 7 — extensão do plano

O planejamento original previa o Dia 7 principalmente como consolidação.

Durante a semana foi adicionada uma extensão coerente com os resultados anteriores:

busca híbrida com Reciprocal Rank Fusion.

Essa extensão não fazia parte do escopo original do Dia 7 e deve ser registrada como tal.

## Busca híbrida

Foi implementado:

`GET /search/hybrid`

A estratégia combina:

- ranking textual;
- ranking semântico.

A fusão utiliza Reciprocal Rank Fusion.

O RRF foi escolhido para evitar somar diretamente sinais com escalas diferentes.

A decisão está registrada no ADR-008.

Os três mecanismos permanecem disponíveis separadamente:

- `GET /search`
- `GET /search/semantic`
- `GET /search/hybrid`

## Testes

Ao final da Semana 4:

`54 passed`

A suíte cobre, entre outras áreas:

- documentos;
- chunking;
- embeddings;
- busca textual;
- busca semântica;
- max_distance;
- RRF;
- busca híbrida;
- contratos HTTP.

Também foram executadas validações end-to-end com PostgreSQL, pgvector e embeddings reais.

## O que consigo explicar agora

Consigo explicar o fluxo:

texto
→ chunk
→ embedding
→ vector(384)
→ persistência
→ query embedding
→ cosine distance
→ ranking
→ top_k
→ max_distance
→ avaliação
→ RRF
→ busca híbrida

Também consigo diferenciar:

ranking ≠ relevância absoluta

top_k ≠ threshold

retrieval ≠ generation

experimento controlado ≠ garantia de produção

## Limitações atuais

Ainda não foram demonstrados:

- desempenho em corpus grande;
- threshold universal;
- melhor modelo de embeddings;
- melhor estratégia de chunking;
- melhor valor de rrf_k;
- necessidade de HNSW ou IVFFlat;
- métricas amplas como Recall@k, MRR ou nDCG;
- superioridade universal da busca híbrida;
- qualidade de geração com LLM.

RAG ainda não foi implementado.

## Consolidação de aprendizado

A semana não terminou apenas com código.

O ciclo completo foi:

estudo
→ implementação
→ testes
→ experimentos
→ documentação
→ materiais de estudo
→ podcasts no NotebookLM
→ revisão
→ roteiro
→ aula gravada

A aula gravada de aproximadamente 20 minutos foi concluída.

## Principal aprendizado

A principal mudança foi deixar de pensar apenas:

"como implementar busca vetorial?"

e passar a separar problemas:

Como representar significado?
→ embeddings

Como persistir?
→ pgvector

Como ordenar?
→ cosine distance

Quantos resultados?
→ top_k

Quando rejeitar?
→ max_distance

Como avaliar?
→ experimento

Como combinar sinais diferentes?
→ RRF

## Próximo passo

Antes de iniciar a Semana 5 e implementar RAG, será concluído o fechamento profissional.

A próxima etapa será:

README e documentação
→ revisão final
→ análise de vagas reais
→ gap analysis
→ posicionamento profissional
→ definição final da Semana 5

O roadmap não deve evoluir apenas porque uma tecnologia parece interessante.

A próxima decisão técnica deve continuar relacionada ao aprendizado e às necessidades observadas no mercado.
