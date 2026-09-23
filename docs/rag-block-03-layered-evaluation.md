# RAG BLOCK 03 — LAYERED EVALUATION

**Status:** infraestrutura de avaliação em camadas concluída; answerability semântica e generation reais ainda não avaliadas

**Objetivo:** separar falhas por camada do pipeline RAG e tornar explícito quando uma camada falhou, foi bloqueada ou ainda não foi avaliada.

---

## 1. Problema

O Bloco 2 criou uma baseline reproduzível de retrieval.

Isso permitiu responder:

- o documento esperado foi recuperado?
- em qual posição?
- documentos proibidos de outro usuário apareceram?
- qual foi o comportamento em `top_k=1` e `top_k=5`?

Mas retrieval sozinho não responde por que uma resposta final do RAG seria correta ou incorreta.

O pipeline possui camadas diferentes:

```text
retrieval
↓
context
↓
answerability
↓
generation
↓
answer + sources
```

Uma falha final pode ter causas diferentes.

Exemplos:

```text
documento correto não recuperado
→ retrieval

evidência recuperada não preservada no contexto
→ context

contexto existe, mas não deveria autorizar geração
→ answerability

geração autorizada, mas resposta não fundamentada
→ generation
```

Sem separar essas camadas, uma métrica única de "RAG quality" esconderia a causa real dos erros.

---

## 2. Objetivo arquitetural

O Bloco 3 introduziu uma classificação causal explícita.

Cada camada pode possuir um dos estados:

```text
PASS
FAIL
BLOCKED
NOT_EVALUATED
```

### PASS

A camada foi efetivamente avaliada e satisfez o contrato medido.

### FAIL

A camada foi avaliada e falhou.

A primeira ocorrência de `FAIL` se torna `first_failure`.

### BLOCKED

Uma camada anterior falhou.

A camada posterior não deve ser interpretada independentemente como sucesso ou falha daquele caso.

### NOT_EVALUATED

A camada não foi medida naquele caso.

Isso não representa falha.

Também não representa sucesso.

---

## 3. FAIL não é NOT_EVALUATED

Uma distinção importante deste bloco foi:

```text
FAIL
→ bloqueia causalmente as camadas posteriores

NOT_EVALUATED
→ não bloqueia uma medição posterior independente
```

Exemplo:

```text
retrieval = NOT_EVALUATED
context = PASS
```

Esse cenário é válido quando o caso não possui critérios de scoring de retrieval, mas o Context Builder ainda pode ser avaliado estruturalmente.

Isso ocorre, por exemplo, em casos `unanswerable` que não possuem documentos esperados nem proibidos para pontuar retrieval.

---

## 4. Contrato de layered evaluation

Foi criado:

```text
evaluation/layered.py
```

Principais contratos:

```text
EvaluationLayer
LayerStatus
LayerEvaluationChecks
LayeredEvaluationResult
```

Camadas atuais:

```text
retrieval
context
answerability
generation
```

O resultado inclui:

```text
retrieval status
context status
answerability status
generation status
first_failure
```

O objetivo de `first_failure` é registrar a primeira falha causal observada.

---

## 5. Context evaluation

Foi criada avaliação estrutural específica para o Context Builder.

O Context Builder continua sendo responsabilidade diferente de retrieval.

```text
retrieval
→ seleciona evidência

context builder
→ organiza a evidência selecionada para as camadas posteriores
```

A avaliação estrutural verifica:

- quantidade de evidências;
- existência de texto;
- preservação das evidências;
- preservação do conteúdo;
- consistência entre presença de resultados e presença de texto.

O resultado é representado por:

```text
ContextEvaluationResult
```

Importante:

```text
context PASS
≠
evidência semanticamente suficiente
```

Um `PASS` nessa camada significa apenas que o Context Builder preservou estruturalmente os resultados recebidos.

---

## 6. Answerability evaluation contract

Foi criado:

```text
evaluation/answerability_evaluation.py
```

Contrato:

```text
AnswerabilityEvaluationResult
```

Campos principais:

```text
evaluated
expected_abstained
observed_abstained
should_abstain
can_generate
reason
semantic_evaluation_used
passed
```

A avaliação reutiliza o comportamento da aplicação:

```text
assess_answerability()
```

Quando não existe evidência:

```text
no_context
↓
should_abstain = true
can_generate = false
```

Esse caso pode ser avaliado deterministicamente.

---

## 7. Semantic answerability

Quando existe contexto, a regra atual da aplicação é:

```text
semantic_evaluation_required
```

Nesse caso existem dois cenários.

### Evaluator disponível

O evaluator recebe:

- pergunta;
- texto do contexto autorizado.

A decisão produzida pode então ser comparada com `expected_abstained`.

### Evaluator indisponível

O resultado é:

```text
evaluated = false
passed = null
```

E a camada fica:

```text
NOT_EVALUATED
```

Isso evita transformar ausência de avaliação semântica em sucesso ou falha artificial.

---

## 8. Avaliação controlada de answerability

O contrato foi validado com evaluators controlados.

Foram cobertos:

- `no_context` com abstention esperada;
- contexto existente sem evaluator;
- decisão semântica controlada permitindo geração;
- decisão semântica controlada exigindo abstention;
- divergência entre decisão observada e expectativa.

Esses testes validam a infraestrutura de avaliação.

Eles não representam qualidade de um semantic evaluator real.

---

## 9. Executor em camadas

Foi criado o executor:

```text
evaluate_layered_case()
```

Fluxo:

```text
EvaluationCase
+
RetrievalObservation
↓
retrieval evaluation
↓
build_rag_context()
↓
context evaluation
↓
answerability evaluation
↓
layered classification
```

O `RagContext` é construído uma única vez e reutilizado.

Isso evita avaliar uma versão do contexto e enviar outra versão para answerability.

---

## 10. Propagação causal

O executor não chama answerability quando existe falha real em uma camada anterior.

Exemplo:

```text
retrieval FAIL
↓
context pode ter resultado estrutural interno
↓
layered context = BLOCKED
↓
answerability = BLOCKED
↓
generation = BLOCKED
```

Outro exemplo:

```text
retrieval PASS
↓
context FAIL
↓
answerability = BLOCKED
↓
generation = BLOCKED
```

Isso preserva a interpretação causal.

---

## 11. Retrieval NOT_EVALUATED

`NOT_EVALUATED` em retrieval não bloqueia as próximas camadas.

Exemplo:

```text
retrieval = NOT_EVALUATED
context = PASS
answerability = NOT_EVALUATED
```

Esse comportamento é importante para os casos `unanswerable`.

Eles podem não possuir um critério de sucesso de retrieval e ainda assim fornecer informação útil sobre as camadas seguintes.

---

## 12. Métricas por camada

Foi criado:

```text
evaluation/layered_metrics.py
```

Para cada camada são agregadas:

```text
total_cases
evaluated_cases
passed_cases
failed_cases
blocked_cases
not_evaluated_cases
pass_rate
```

A definição de `evaluated_cases` é:

```text
PASS + FAIL
```

A taxa é calculada como:

```text
pass_rate
=
PASS / (PASS + FAIL)
```

`BLOCKED` e `NOT_EVALUATED` ficam fora do denominador.

Isso evita punir ou inflar uma camada com casos que não foram efetivamente medidos.

---

## 13. Pass rate sem casos avaliados

Internamente a função genérica de rate continua retornando `0.0` para denominador zero.

Na CLI, entretanto, uma camada com:

```text
evaluated_cases = 0
```

é apresentada como:

```text
pass_rate: N/A
```

Isso evita a interpretação incorreta de `0.00%` como se a camada tivesse falhado em todos os casos.

---

## 14. First failure

A summary também registra:

```text
first_failure_counts
cases_with_failure
no_failure_observed_cases
observed_failure_rate
```

O termo adotado foi:

```text
no_failure_observed_cases
```

e não:

```text
successful_cases
```

porque ausência de falha observada não significa necessariamente pipeline inteiro aprovado.

Um caso pode simplesmente conter camadas `NOT_EVALUATED`.

---

## 15. CLI de layered evaluation

Foi criado:

```text
evaluation/run_layered.py
```

Ele é separado de:

```text
evaluation/run_retrieval.py
```

A separação preserva responsabilidades claras.

### Retrieval runner

```text
dataset
↓
retrieval real
↓
retrieval metrics
```

### Layered runner

```text
dataset
↓
retrieval real
↓
context real
↓
answerability disponível
↓
layered classification
↓
layered summary
```

Não foi adicionada uma série de flags ao runner de retrieval para fazê-lo assumir responsabilidades de outras camadas.

---

## 16. Execução real

Comando utilizado:

```text
python -m evaluation.run_layered --top-k 5
```

Configuração:

```text
top_k = 5
max_distance = None
semantic_evaluator = disabled
generation_evaluation = disabled
```

Infraestrutura reutilizada:

- PostgreSQL;
- pgvector;
- SentenceTransformer;
- embeddings reais;
- hybrid retrieval;
- RRF;
- Context Builder real;
- corpus versionado;
- dataset de 50 casos.

---

## 17. Resultado de retrieval

A execução produziu:

```text
scored_cases: 37
scored_pass_rate: 100.00%
expected_case_hit@5: 100.00%
expected_document_recall@5: 100.00%
forbidden_document_absence: 100.00%
```

Resumo da camada:

| Estado | Casos |
|---|---:|
| PASS | 37 |
| FAIL | 0 |
| BLOCKED | 0 |
| NOT_EVALUATED | 13 |
| **Total** | **50** |

Casos efetivamente avaliados:

```text
37
```

Pass rate entre casos avaliados:

```text
100.00%
```

Os 13 casos `NOT_EVALUATED` são os casos sem critérios de scoring de retrieval.

Isso não significa que retrieval falhou nesses casos.

---

## 18. Resultado de context

A camada de context produziu:

| Estado | Casos |
|---|---:|
| PASS | 50 |
| FAIL | 0 |
| BLOCKED | 0 |
| NOT_EVALUATED | 0 |
| **Total** | **50** |

Casos avaliados:

```text
50
```

Pass rate estrutural:

```text
100.00%
```

Interpretação correta:

> Nos 50 casos da execução controlada, o Context Builder preservou estruturalmente a evidência recebida do retrieval de acordo com os checks definidos neste bloco.

Não interpretar como:

> Os 50 contextos eram semanticamente suficientes para responder.

Essa propriedade pertence à camada de answerability.

---

## 19. Resultado de answerability

A execução real produziu:

| Estado | Casos |
|---|---:|
| PASS | 0 |
| FAIL | 0 |
| BLOCKED | 0 |
| NOT_EVALUATED | 50 |
| **Total** | **50** |

Casos avaliados:

```text
0
```

Pass rate:

```text
N/A
```

Esse resultado é esperado com a configuração atual.

Com:

```text
top_k = 5
max_distance = None
```

todos os casos receberam algum contexto autorizado.

Inclusive casos `unanswerable` receberam vizinhos semanticamente próximos.

Portanto nenhum caso caiu no caminho determinístico:

```text
no_context
↓
abstention
```

Todos os casos com contexto chegaram a:

```text
semantic_evaluation_required
```

Como ainda não existe semantic evaluator real configurado:

```text
answerability = NOT_EVALUATED
```

---

## 20. Retrieval não decide answerability

A execução demonstrou diretamente uma distinção importante do pipeline:

```text
retrieval encontrou candidatos
≠
há evidência suficiente para responder
```

Os casos `unanswerable` são o exemplo principal.

Hybrid retrieval continua retornando os candidatos autorizados semanticamente mais próximos.

Isso é comportamento de retrieval.

A decisão:

```text
a evidência é suficiente?
```

pertence à camada de answerability.

Portanto não deve ser inferida a partir da simples existência de resultados.

---

## 21. Resultado de generation

A camada de generation produziu:

| Estado | Casos |
|---|---:|
| PASS | 0 |
| FAIL | 0 |
| BLOCKED | 0 |
| NOT_EVALUATED | 50 |
| **Total** | **50** |

Casos avaliados:

```text
0
```

Pass rate:

```text
N/A
```

Nenhum provider LLM real foi avaliado neste bloco.

Portanto ainda não foram medidas:

- qualidade da resposta;
- groundedness;
- fidelidade ao contexto;
- completude;
- qualidade textual;
- claim-level support.

---

## 22. First failure observado

Resultado:

```text
retrieval: 0
context: 0
answerability: 0
generation: 0

cases_with_failure: 0
no_failure_observed_cases: 50
observed_failure_rate: 0.00%
```

Esse resultado exige cuidado.

Não significa:

```text
50 pipelines completos passaram
```

Significa apenas:

```text
nenhuma camada efetivamente avaliada registrou FAIL
```

Answerability e generation permaneceram `NOT_EVALUATED`.

Portanto:

```text
no_failure_observed_cases
≠
complete_pipeline_success
```

---

## 23. Relação com o Bloco 2

O Bloco 2 já havia mostrado:

```text
top_k=1
→ 92.59% Hit@1 / Recall@1

top_k=5
→ 100% Hit@5 / Recall@5
```

As duas falhas em rank 1 eram competição de ranking.

No Bloco 3 foi utilizado:

```text
top_k=5
```

Isso corresponde ao caminho atual do RAG e permite que as camadas posteriores recebam um conjunto mais amplo de evidências candidatas.

O resultado não elimina o diagnóstico anterior de ranking.

Ele apenas fornece a entrada para avaliação das próximas camadas.

---

## 24. Cross-user

Na execução com `top_k=5`:

```text
forbidden_document_absence = 100%
```

O resultado continua consistente com o benchmark anterior.

Nos casos controlados cross-user, documentos proibidos não apareceram nos resultados recuperados.

Como ownership filtering ocorre antes das camadas posteriores:

```text
owner filtering
↓
retrieval
↓
context
↓
answerability
↓
generation
```

a evidência proibida também não é selecionada pelo Context Builder nesses casos.

Esse resultado representa evidência positiva no benchmark controlado.

Não representa prova de segurança de produção.

---

## 25. Validação automatizada

Durante a evolução do bloco foram criados testes específicos para:

- contrato das camadas;
- semântica de `BLOCKED`;
- semântica de `NOT_EVALUATED`;
- Context Builder;
- answerability evaluation;
- semantic evaluator controlado;
- integração retrieval → context → answerability;
- primeira falha causal;
- métricas agregadas por camada.

Ao final da implementação desta infraestrutura:

```text
171 passed
2 warnings conhecidos
```

Os warnings não foram introduzidos pelo Bloco 3.

---

## 26. Limitações

### Semantic answerability

Ainda não existe evaluator semântico real configurado.

Portanto:

```text
answerability real
→ ainda não medida
```

### Generation

Ainda não existe provider LLM real avaliado pelo harness em camadas.

Portanto:

```text
generation quality
→ ainda não medida
```

### Groundedness

Groundedness ainda não foi medida.

### Reference answer

O `reference_answer` do dataset ainda não está sendo utilizado para avaliar geração.

### Sources

Sources continuam representando provenance do contexto.

Ainda não existe validação claim-level.

### Unanswerable

Com `max_distance=None`, retrieval retorna candidatos mesmo quando a pergunta deveria terminar em abstention.

Esse comportamento reforça a necessidade da camada de answerability.

### Corpus

O corpus continua controlado e composto por 18 documentos.

### Chunking

Os documentos do benchmark permanecem deliberadamente abaixo do `chunk_size=500`.

Portanto ainda não há avaliação formal de competição entre múltiplos chunks do mesmo documento.

### Idioma

O benchmark continua majoritariamente em inglês.

### Produção

Os resultados não representam prova de performance, segurança ou confiabilidade em produção.

---

## 27. Interpretação correta

Pode ser afirmado:

> O MKA possui agora um harness capaz de classificar separadamente retrieval, context, answerability e generation como PASS, FAIL, BLOCKED ou NOT_EVALUATED, preservando a primeira falha causal observada.

Também pode ser afirmado:

> Em uma execução controlada com 50 casos e `top_k=5`, os 37 casos pontuáveis de retrieval passaram, com 100% de Hit@5/Recall@5 e 100% de ausência de documentos proibidos. O Context Builder passou nos 50 checks estruturais definidos.

Também pode ser afirmado:

> Answerability semântica e generation não foram avaliadas nessa execução. Os 50 casos ficaram como NOT_EVALUATED nessas camadas porque ainda não existe semantic evaluator real nem avaliação de geração real no harness.

Não afirmar:

- RAG completo possui 100% de acerto;
- answerability possui 0% ou 100% de qualidade;
- generation possui 0% ou 100% de qualidade;
- groundedness foi validada;
- 50 de 50 pipelines completos passaram;
- segurança foi comprovada em produção;
- o sistema está production-ready.

---

## 28. Resultado arquitetural

Antes:

```text
resultado final ruim
↓
causa pouco explícita
```

Depois do Bloco 3:

```text
retrieval
↓
context
↓
answerability
↓
generation

cada camada
↓
PASS / FAIL / BLOCKED / NOT_EVALUATED

+
first_failure
```

Isso transforma a evaluation de uma simples métrica final em um instrumento de diagnóstico por camada.

---

## 29. Status do Bloco 3

Infraestrutura planejada para separar as camadas:

```text
CONCLUÍDA
```

Medições atuais:

```text
retrieval
→ MEDIDO

context estrutural
→ MEDIDO

answerability controlada
→ TESTADA

answerability semântica real
→ NÃO MEDIDA

generation real
→ NÃO MEDIDA

groundedness
→ NÃO MEDIDA
```

Portanto o Bloco 3 fecha a infraestrutura necessária para distinguir as camadas, mas não deve ser usado para afirmar qualidade das camadas que ainda dependem de providers reais.

---

## 30. Próximo gate

### BLOCO 4 — One Real LLM Provider

Objetivo:

Substituir pelo menos uma fronteira controlada por um provider LLM real, mantendo:

```text
contrato
↓
provider adapter
↓
tratamento explícito de falhas
↓
testes controlados
↓
experimento real separado
```

O próximo bloco deve permitir avançar de:

```text
answerability = NOT_EVALUATED
generation = NOT_EVALUATED
```

para medições reais e reproduzíveis.

A introdução do provider não deve apagar a separação construída neste bloco.

O pipeline deve continuar distinguindo:

```text
retrieval failure
context failure
answerability failure
generation failure
provider failure
```
