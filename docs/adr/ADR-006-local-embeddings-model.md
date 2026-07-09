# ADR-006 - Modelo local de embeddings

## Status

Aceita

## Contexto

O projeto Mission Knowledge Assistant evoluiu, até a Semana 3, para uma base com documentos persistidos, chunks gerados automaticamente e busca textual simples usando `ILIKE`.

A busca textual é útil para correspondência literal de palavras, mas não entende significado. Para preparar o projeto para busca semântica e, posteriormente, RAG, é necessário representar chunks e queries como vetores numéricos comparáveis.

A Semana 4 tem como objetivo introduzir embeddings e busca vetorial com pgvector, mantendo o foco em aprendizado, validação local e controle de escopo.

## Decisão

Utilizar o modelo local `sentence-transformers/all-MiniLM-L6-v2` para gerar embeddings de texto.

O modelo será usado inicialmente para gerar embeddings de chunks e queries.

Cada embedding gerado por esse modelo possui 384 dimensões.

## Motivos

- O modelo roda localmente, sem depender de API externa.
- Não há custo por requisição durante a fase de aprendizado.
- O modelo é leve o suficiente para validação local em ambiente de desenvolvimento.
- A dimensão de 384 vetores é adequada para começar a integrar com pgvector.
- A decisão permite entender o pipeline completo antes de introduzir provedores externos.
- O modelo é suficiente para validar conceitos de busca semântica, similaridade e recuperação de chunks.

## Alternativas consideradas

### Usar API externa de embeddings

Adiada para uma etapa futura.

APIs externas podem oferecer modelos mais robustos e melhor qualidade semântica, mas adicionam custo, latência, dependência externa, gestão de credenciais e maior complexidade operacional.

Neste momento, o objetivo é entender o fluxo de embeddings de ponta a ponta antes de terceirizar essa etapa.

### Usar outro modelo local maior

Rejeitada neste momento para evitar custo computacional maior e complexidade prematura.

A prioridade da Semana 4 é validar arquitetura, persistência e busca vetorial, não otimizar qualidade de embeddings.

### Continuar apenas com busca textual

Rejeitada porque a busca textual não resolve bem consultas por significado.

O projeto precisa evoluir para recuperação semântica para preparar a base de RAG.

## Trade-offs

Usar um modelo local reduz custo e dependência externa, mas pode oferecer qualidade inferior a modelos comerciais maiores.

Também adiciona dependências relevantes ao ambiente, como `sentence-transformers`, `transformers`, `torch` e bibliotecas associadas.

Como os embeddings ficam vinculados ao modelo usado, uma troca futura de modelo pode exigir regenerar embeddings já persistidos.

A dimensão do embedding também passa a ser uma decisão arquitetural importante. Como o modelo gera vetores de 384 dimensões, a coluna vetorial futura no banco deverá respeitar essa dimensão, por exemplo `vector(384)`.

## Consequências

O projeto passa a ter uma decisão explícita para geração local de embeddings.

A Semana 4 usará embeddings de 384 dimensões como base para integração com pgvector.

Os embeddings serão associados aos chunks, não aos documentos completos, porque o chunk é a unidade principal de recuperação.

A busca textual com `ILIKE` não será removida imediatamente. Ela continuará útil para casos de correspondência literal, nomes próprios, códigos, siglas e termos exatos.

Essa decisão prepara o projeto para evoluir da busca textual para busca semântica e, posteriormente, para RAG com LLM.

## Validação

Foi criado um script de validação em `scripts/test_embeddings.py`.

O script valida:

- carregamento do modelo `sentence-transformers/all-MiniLM-L6-v2`;
- geração de embeddings com 384 dimensões;
- comparação de similaridade entre frases relacionadas e não relacionadas.

Resultado observado:

```text
Embedding matrix shape: (3, 384)
Embedding dimensions: 384

Artemis / lunar mission: 0.6031
Artemis / PostgreSQL: 0.1982

Embedding validation completed successfully.
