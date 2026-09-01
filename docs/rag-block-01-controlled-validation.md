# RAG Block 01 — Controlled Validation

**Data:** 31/08/2026
**Branch:** `rag-block-01-controlled-validation`

## Objetivo

Consolidar os comportamentos fundamentais do pipeline RAG antes da integração com um provider LLM real.

Este bloco não adiciona capacidade nova ao RAG.

Ele organiza e valida explicitamente comportamentos que já haviam sido implementados progressivamente.

---

## Matriz de validação

| Caso | Comportamento esperado | Evidência automatizada | Resultado |
|---|---|---|---|
| 1 | Sem contexto autorizado → abstention | `test_rag_answer_abstains_when_no_authorized_context` | PASS |
| 2 | Contexto existe, mas não há decisão semântica suficiente → abstention mantendo sources | `test_rag_answer_uses_context_evidence_as_sources` | PASS |
| 3 | Decisão positiva controlada → generation + sources | `test_rag_answer_generates_when_answerability_allows` e `test_rag_answer_runs_semantic_evaluation_before_generation` | PASS |
| 4 | Provider indisponível → HTTP 503 genérico | quatro testes específicos em `test_rag_route.py` | PASS |
| 5 | Evidência de outro usuário → excluída antes de context/sources | `test_rag_answer_keeps_other_user_content_out_of_context_and_sources` | PASS |

---

## Caso 1 — Sem contexto

Comportamento observado:

```text
answer = null
abstained = true
sources = []
```

Isso representa abstention normal por ausência de contexto autorizado.

Não representa falha operacional.

---

## Caso 2 — Contexto sem decisão semântica suficiente

O fato de existir contexto não significa que existe evidência suficiente para responder.

Fluxo:

```text
context exists
↓
semantic evaluation required
↓
generation not allowed
↓
abstention
```

As sources continuam representando a evidence selecionada pelo Context Builder.

Regra:

```text
retrieval success
≠
answerability
```

O teste correspondente agora verifica explicitamente:

```python
assert response.json()["answer"] is None
assert response.json()["abstained"] is True
```

---

## Caso 3 — Geração positiva controlada

Os testes usam decisões e generators controlados.

Fluxo validado:

```text
authorized retrieval
↓
context
↓
positive answerability decision
↓
generation
↓
answer + sources
```

Também foi validado que o semantic evaluator recebe:

- a pergunta;
- o contexto autorizado.

A decisão semântica positiva é propagada para a geração.

Importante:

Esse caminho utiliza fakes em ambiente controlado.

Ainda não existe semantic evaluator real nem provider LLM real configurado.

---

## Caso 4 — Provider failure

Falhas operacionais conhecidas são representadas por:

`ProviderUnavailableError`

Na fronteira HTTP elas são convertidas para:

`503 Service Unavailable`

Mensagem pública:

`RAG provider is temporarily unavailable.`

Pontos cobertos:

1. resolução do semantic evaluator;
2. execução da avaliação semântica;
3. resolução do generator;
4. execução da geração.

Regra:

```text
abstention
≠
provider failure
```

Detalhes internos do provider não são expostos ao cliente.

Erros genéricos não são capturados amplamente como se fossem indisponibilidade de provider.

---

## Caso 5 — Cross-user isolation

O teste cria documentos pertencentes a dois usuários.

O documento proibido possui match semântico mais forte.

Mesmo assim:

- não entra no contexto;
- não chega ao semantic evaluator;
- não aparece nas sources.

Fluxo preservado:

```text
owner filtering
↓
ranking
↓
top_k
↓
context
↓
answerability
```

Isso demonstra isolamento em experimento controlado.

Não representa prova de segurança em produção.

---

## Gap encontrado

Foi encontrado apenas um gap de explicitude no teste:

`test_rag_answer_uses_context_evidence_as_sources`

O teste já verificava:

- `answer is None`;
- sources provenientes de `context.evidence`.

Foi adicionada:

```python
assert response.json()["abstained"] is True
```

Nenhuma alteração em código de produção foi necessária.

---

## Validação

Validação focada:

```text
12 passed, 1 warning
```

Suíte completa:

```text
124 passed, 2 warnings
```

Warnings permanecem conhecidos e não são causados por este bloco.

---

## Resultado

Os cinco comportamentos planejados para o Block 01 possuem evidência automatizada explícita.

Não foi identificada necessidade de adicionar nova implementação ao pipeline RAG.

O resultado principal deste bloco foi:

```text
comportamentos existentes
↓
inspeção
↓
matriz explícita
↓
gap mínimo encontrado
↓
assertion adicionada
↓
validação completa
```

---

## Limitação

Este bloco valida contratos e comportamento controlado.

Ele ainda não mede qualidade semântica real porque:

- não existe semantic evaluator real;
- não existe provider LLM real;
- ainda não existe dataset formal de evaluation.

Esses pontos pertencem aos próximos blocos.

---

## Próximo gate

### BLOCO 2 — Evaluation Harness

Objetivo:

Criar uma avaliação reproduzível sobre dataset fixo e separar:

```text
testes de software
≠
avaliação de qualidade do sistema
```
