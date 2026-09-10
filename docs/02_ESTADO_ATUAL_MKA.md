# ESTADO ATUAL DO MKA

**Última atualização:** 09/09/2026
**Fonte de verdade técnica:** repositório Git

---

## 1. Baseline confirmado

- Main: `b4b1b50`
- Último merge: PR #49 — RAG Block 01 Controlled Validation
- Branch atual: `rag-block-02-evaluation-harness`
- Base documental da branch antes do fechamento final: `37f25cc`
- Alembic: `1b2ec7d5f630 (head)`
- Testes: `147 passed, 2 warnings`
- Evaluation específica: `23 passed`
- Dataset atual: `50 casos`
- Corpus de evaluation atual: `18 documentos`

---

## 2. Warnings conhecidos

### PostgreSQL collation

O banco `mission_knowledge` foi criado com collation `2.41`, enquanto o ambiente atual fornece `2.36`.

É uma dívida técnica conhecida e não deve ser alterada casualmente durante outro bloco.

### TestClient / httpx

Existe depreciação conhecida relacionada ao Starlette TestClient/httpx.

### HTTP 413

`HTTP_413_REQUEST_ENTITY_TOO_LARGE` está deprecated.

Substituição futura:

`HTTP_413_CONTENT_TOO_LARGE`

Nenhum desses warnings bloqueia o trabalho atual.

---

## 3. Stack consolidada

### Backend

- Python
- FastAPI
- SQLModel
- PostgreSQL
- Alembic

### Infraestrutura e qualidade

- Docker Compose
- Pytest
- Git
- GitHub

### Retrieval / IA

- sentence-transformers
- `sentence-transformers/all-MiniLM-L6-v2`
- embeddings locais de 384 dimensões
- pgvector
- busca textual
- busca semântica
- busca híbrida
- Reciprocal Rank Fusion (RRF)

---

## 4. Security Slice

Status: **concluído**

Implementado:

- usuários;
- password hashing com Argon2;
- autenticação;
- JWT;
- `/auth/login`;
- `/auth/me`;
- autorização;
- ownership de documentos;
- isolamento entre usuários;
- testes cross-user.

Regra central:

```text
Document.owner_id
↓
vem do usuário autenticado
↓
nunca do payload público
```

Autenticação identifica.

Autorização decide acesso.

---

## 5. Retrieval

Status: **implementado e com baseline de evaluation**

Existem:

- textual retrieval;
- semantic retrieval;
- hybrid retrieval;
- `top_k`;
- `max_distance`;
- RRF;
- ownership filtering.

Regra crítica:

```text
authorization / owner filtering
↓
ranking
↓
top_k
```

Filtrar antes do ranking protege:

1. confidencialidade;
2. correção do retrieval.

Baseline controlada atual:

```text
18 documentos
50 casos
```

Resultados:

```text
top_k=1
expected_case_hit@1 = 92.59%
expected_document_recall@1 = 92.59%
forbidden_document_absence = 100.00%

top_k=5
expected_case_hit@5 = 100.00%
expected_document_recall@5 = 100.00%
forbidden_document_absence = 100.00%
```

Essas métricas pertencem ao benchmark controlado versionado.

Não representam produção.

---

## 6. Pipeline RAG atual

```text
AUTHENTICATION
↓
AUTHORIZATION
↓
RETRIEVAL
↓
CONTEXT BUILDER
↓
ANSWERABILITY
├─ não → ABSTENTION
└─ sim → GENERATION
↓
ANSWER + SOURCES
```

Endpoint:

`POST /rag/answer`

Resposta:

- `answer`;
- `abstained`;
- `sources`.

---

## 7. Context Builder

Existe uma camada explícita entre retrieval e geração.

Responsabilidades atuais:

- receber resultados autorizados;
- preservar ordem;
- montar contexto;
- preservar evidence/provenance.

Limitações atuais:

- sem token budget;
- sem truncation sofisticado;
- sem deduplicação sofisticada.

---

## 8. Answerability

Sem evidência:

```text
should_abstain = True
can_generate = False
reason = no_context
```

Com evidência:

```text
should_abstain = False
can_generate = False
reason = semantic_evaluation_required
```

Regra:

```text
contexto existente
≠
pergunta respondível
```

---

## 9. Semantic Answerability

Existe uma boundary independente.

O provider padrão ainda retorna `None`.

Portanto:

- não existe evaluator semântico real;
- o comportamento default permanece conservador;
- caminhos positivos são atualmente demonstrados por testes controlados.

O Bloco 2 não mede ainda a qualidade real dessa camada.

---

## 10. Generator Boundary

Existe contrato provider-agnostic:

- `GenerationRequest`;
- `GenerationResult`;
- `Generator`;
- `generate_answer()`.

Ainda não existe provider LLM real configurado.

Nenhuma API key real deve ser versionada.

---

## 11. Generation Gate

Generation só pode acontecer quando:

```text
decision.can_generate == True
```

Caso contrário, o sistema se abstém.

---

## 12. Segurança cross-user no RAG e retrieval

Existe evidência automatizada de que evidência pertencente a outro usuário:

- não entra no contexto;
- não entra nas sources;
- não consome o `top_k` autorizado.

No benchmark ampliado do Bloco 2:

```text
10 casos cross-user
forbidden_document_absence = 100%
```

Isso é evidência de experimento controlado.

Não é prova de segurança de produção.

---

## 13. Provider failures

Existe:

`ProviderUnavailableError`

Falhas operacionais conhecidas são convertidas na fronteira HTTP para:

`503 Service Unavailable`

Mensagem pública:

`RAG provider is temporarily unavailable.`

São tratados:

1. resolução do semantic evaluator;
2. execução do semantic evaluator;
3. resolução do generator;
4. execução da geração.

Regra:

```text
abstention
≠
provider failure
```

Não existe captura ampla de `Exception` ou `RuntimeError` para mascarar bugs genéricos.

---

## 14. Evaluation Harness

Status: **concluído**

Estrutura:

```text
evaluation/
├── corpus.py
├── dataset.py
├── metrics.py
├── models.py
├── retrieval_executor.py
├── retrieval_metrics.py
├── run_retrieval.py
├── runner.py
└── data/
    ├── cases.jsonl
    └── corpus.jsonl
```

Separação adotada:

```text
tests/
→ contratos e regressões do software

evaluation/
→ medição de comportamento sobre dataset fixo
```

Dataset atual:

| Categoria | Casos |
|---|---:|
| Answerable | 20 |
| Unanswerable | 13 |
| Cross-user | 10 |
| Difficult | 7 |
| **Total** | **50** |

Corpus:

```text
18 documentos
```

---

## 15. Retrieval Evaluation observada

### top_k=1

```text
scored_cases = 37
scored_pass_rate = 94.59%
expected_case_hit@1 = 92.59%
expected_document_recall@1 = 92.59%
forbidden_document_absence = 100.00%
```

Dos 27 casos com documento esperado:

```text
25/27
→ documento esperado em rank 1
```

Falhas de rank 1:

```text
eval-003
esperado: rag-abstention
observado rank 1: sources-provenance

eval-008
esperado: rag-abstention
observado rank 1: sources-provenance
```

### top_k=5

```text
scored_pass_rate = 100.00%
expected_case_hit@5 = 100.00%
expected_document_recall@5 = 100.00%
forbidden_document_absence = 100.00%
```

Posições dos dois casos anteriores:

```text
eval-003
rag-abstention → rank 2

eval-008
rag-abstention → rank 3
```

Diagnóstico:

```text
evidência esperada estava presente
↓
outro documento semanticamente próximo ficou acima
↓
problema observado é principalmente de ranking
```

Nenhum tuning foi feito para esconder essas falhas depois da medição.

Relatório:

`docs/rag-block-02-evaluation-harness.md`

---

## 16. O que ainda NÃO está implementado ou medido

Ainda faltam:

- provider LLM real;
- semantic evaluator real;
- avaliação separada de retrieval vs generation;
- groundedness medido;
- qualidade real de geração;
- claim-level validation;
- avaliação formal em português/cross-language;
- benchmark com documentos multi-chunk;
- observabilidade final;
- CI/CD final;
- deploy demonstrável;
- release V1;
- case study final;
- vídeo final de portfólio.

Não afirmar que o sistema está production-ready.

---

## 17. Narrativa profissional

Usar:

> Tenho uma base backend real e estou evoluindo progressivamente para aplicações de IA/LLM.

Não usar:

- especialista em RAG;
- AI Engineer experiente;
- sistema production-ready;
- segurança comprovada em produção.

As métricas do projeto devem sempre carregar o contexto do benchmark em que foram medidas.

---

## 18. Modelo de trabalho atual

A unidade principal é:

```text
BLOCO DE ENTREGA
```

Fluxo:

```text
problema
→ conceito
→ decisão
→ implementação
→ testes
→ validação
→ medição
→ limitações
→ documentação
→ explicação
```

---

## 19. BLOCO 1 — Validação Controlada do Pipeline RAG

Status: **concluído**

Resultado:

Os cinco comportamentos definidos para o bloco possuem evidência automatizada explícita:

1. sem contexto autorizado → abstention;
2. contexto sem decisão semântica suficiente → abstention + sources;
3. decisão positiva controlada → generation + sources;
4. provider indisponível → HTTP 503;
5. evidência cross-user → excluída do contexto e das sources.

Relatório:

`docs/rag-block-01-controlled-validation.md`

---

## 20. BLOCO 2 — Evaluation Harness

Status: **concluído**

Entregas principais:

- dataset versionado;
- corpus versionado;
- 50 casos;
- 18 documentos;
- runner;
- métricas;
- segmentação por categoria;
- executor de retrieval;
- PostgreSQL real;
- pgvector real;
- embeddings reais;
- hybrid retrieval real;
- baseline `top_k=1`;
- baseline `top_k=5`;
- diagnóstico de ranking;
- casos cross-user;
- testes de integridade do dataset;
- relatório técnico.

Testes:

```text
147 passed
2 warnings
```

Resultado principal:

```text
Hit@1 / Recall@1 = 92.59%
Hit@5 / Recall@5 = 100.00%
Forbidden document absence = 100.00%
```

Esses resultados são de benchmark controlado.

---

## 21. Próximo bloco

### BLOCO 3 — Retrieval vs Generation Evaluation

Objetivo:

Separar falhas por camada.

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

Próxima pergunta técnica:

```text
quando uma resposta falha,
em qual camada ocorreu a falha?
```

O próximo bloco não deve introduzir tecnologias aleatórias.

Ele deve usar o harness já construído para tornar os erros do pipeline observáveis e classificáveis.
