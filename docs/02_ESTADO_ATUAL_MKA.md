# ESTADO ATUAL DO MKA

**Última atualização:** 31/08/2026
**Fonte de verdade técnica:** repositório Git

---

## 1. Baseline confirmado

- Main: `f30c24d`
- Último merge: PR #48 — RAG Day 10 Provider Failures
- Commit funcional: `b775552`
- Branch atual: `rag-block-01-controlled-validation`
- Alembic: `1b2ec7d5f630 (head)`
- Testes: `124 passed, 2 warnings`
- Working tree antes do novo bloco: `clean`

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
- embeddings locais
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

Status: **implementado**

Existem:

- textual retrieval;
- semantic retrieval;
- hybrid retrieval;
- `top_k`;
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

## 12. Segurança cross-user no RAG

Existe teste controlado mostrando que uma evidência pertencente a outro usuário, mesmo sendo semanticamente mais forte:

- não entra no contexto;
- não entra nas sources;
- não consome o `top_k` autorizado.

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

## 14. O que ainda NÃO está implementado

Ainda faltam:

- provider LLM real;
- semantic evaluator real;
- evaluation harness;
- dataset formal de evaluation;
- métricas reproduzíveis do RAG;
- groundedness medido;
- observabilidade final;
- CI/CD final;
- deploy demonstrável;
- release V1;
- case study final;
- vídeo final de portfólio.

Não afirmar que o sistema está production-ready.

---

## 15. Narrativa profissional

Usar:

> Tenho uma base backend real e estou evoluindo progressivamente para aplicações de IA/LLM.

Não usar:

- especialista em RAG;
- AI Engineer experiente;
- sistema production-ready;
- segurança comprovada em produção.

---

## 16. Modelo de trabalho atual

A partir de 31/08/2026, a unidade principal deixa de ser micro-"Days".

Usamos:

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

## 17. Bloco atual

### BLOCO 1 — Validação Controlada do Pipeline RAG

Status: **concluído**

Resultado:

Os cinco comportamentos definidos para o bloco possuem evidência automatizada explícita:

1. sem contexto autorizado → abstention;
2. contexto sem decisão semântica suficiente → abstention + sources;
3. decisão positiva controlada → generation + sources;
4. provider indisponível → HTTP 503;
5. evidência cross-user → excluída do contexto e das sources.

Gap encontrado:

Foi adicionada uma assertion explícita de:

`abstained is True`

ao teste de contexto com sources.

Nenhuma alteração de comportamento em código de produção foi necessária.

Relatório:

`docs/rag-block-01-controlled-validation.md`

### Próximo bloco

**BLOCO 2 — Evaluation Harness**

Objetivo:

Criar uma avaliação reproduzível sobre dataset fixo, separando testes de software de avaliação de qualidade semântica.
