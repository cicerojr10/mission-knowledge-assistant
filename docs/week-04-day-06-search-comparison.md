# Semana 4 — Dia 6
## Comparação entre busca textual e busca semântica

## Objetivo

Comparar a busca textual e a busca semântica do Mission Knowledge Assistant usando consultas controladas.

A avaliação deve observar:

- correspondência literal;
- paráfrases;
- intenção semântica;
- identificadores exatos;
- consultas híbridas;
- consultas sem conteúdo relevante;
- efeito de `top_k`;
- efeito de `max_distance`.

## Princípio de avaliação

Os resultados esperados são definidos antes da execução.

Isso evita alterar a interpretação depois de observar os resultados.

```text
expectativa definida antes
→ execução
→ registro do resultado
→ análise

## Resultado da baseline

Configuração:

```text
busca textual:
ILIKE com a consulta completa

busca semântica:
top_k = 5
max_distance = None

## Comparação de thresholds

Foram avaliados três valores de `max_distance`, sempre com:

```text
top_k = 5

## Comparação de top_k

O efeito de `top_k` foi avaliado sem `max_distance`.

Foram testados:

```text
top_k = 1
top_k = 3
top_k = 5