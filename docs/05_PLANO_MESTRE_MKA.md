# MISSION KNOWLEDGE ASSISTANT — PLANO MESTRE

**Baseline:** 31/08/2026
**Fonte de verdade técnica:** Git
**Estado operacional:** `docs/02_ESTADO_ATUAL_MKA.md`

---

## 1. Norte profissional

Objetivo imediato:

- Backend Developer;
- Python Developer;
- Junior Software Engineer com foco backend.

Evolução:

```text
backend sólido
↓
integrações externas
↓
aplicações IA/LLM
↓
RAG
↓
evaluation
```

Narrativa:

> Tenho uma base backend real e estou evoluindo progressivamente para aplicações de IA/LLM.

Engenharia de software vem antes da adição de tecnologias de IA.

---

## 2. Objetivo da MKA V1

Demonstrar:

```text
usuário autenticado
↓
autorização
↓
retrieval autorizado
↓
contexto autorizado
↓
answerability
├─ abstention
└─ generation
↓
answer + sources
↓
evaluation
↓
observabilidade
↓
CI/CD
↓
deploy
```

A V1 não precisa de:

- frontend complexo;
- Kafka;
- Kubernetes;
- múltiplos providers;
- agentes;
- live demo pública com LLM pago.

---

## 3. Estratégia por horizonte

### Curto prazo

Horizonte inicial:

**31/08/2026 → aproximadamente 11/09/2026**

Objetivo:

**fechar o núcleo da MKA V1**

Unidade:

**8 blocos de entrega**

A data é meta operacional, não promessa rígida.

---

### Médio prazo

Horizonte:

**1–3 meses após a V1**

Objetivo:

**converter projeto em empregabilidade**

Frentes:

- Python;
- SQL;
- APIs;
- backend;
- debugging;
- testes;
- Docker;
- Git;
- CI/CD;
- entrevistas;
- candidaturas;
- comunicação técnica.

---

### Longo prazo

Horizonte:

**3–12+ meses**

Direção:

```text
backend sólido
↓
integrações externas
↓
RAG / LLM aplicado
↓
evaluation
↓
observabilidade de IA
↓
arquiteturas mais complexas quando necessárias
```

Nova tecnologia só entra para resolver problema concreto.

---

# 4. Roadmap da V1

## BLOCO 1 — Validação controlada do pipeline RAG

Objetivo:

Consolidar os comportamentos já implementados.

Casos obrigatórios:

1. sem contexto → abstention;
2. contexto sem decisão semântica → abstention;
3. decisão positiva → generation + sources;
4. provider indisponível → 503;
5. cross-user → nenhuma evidência proibida.

Entregáveis:

- matriz de validação;
- gaps explícitos;
- testes necessários;
- suíte verde.

---

## BLOCO 2 — Evaluation Harness

Objetivo:

Construir avaliação reproduzível.

Dataset inicial proposto:

**50 casos**

Cobertura planejada:

| Categoria | Meta |
|---|---:|
| Answerable | 40% |
| Unanswerable / abstention | 25% |
| Cross-user / security | 20% |
| Difíceis / ambíguos / ruidosos | 15% |

Esses percentuais representam desenho experimental.

Não representam distribuição do mundo real.

Entregáveis:

- dataset versionado;
- expected outcomes;
- runner;
- relatório reproduzível.

---

## BLOCO 3 — Retrieval vs Generation Evaluation

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
```

Métricas propostas:

- Recall@5;
- cobertura de evidência;
- abstention precision;
- groundedness;
- sources.

Metas iniciais propostas no corpus controlado:

| Métrica | Meta |
|---|---:|
| Recall@5 | ≥ 0,90 |
| Groundedness | ≥ 0,85 |
| Abstention precision | ≥ 0,90 |
| Respostas geradas com sources | 100% |
| Casos cross-user sem evidência proibida | 100% |

São metas de planejamento.

Só se tornam resultados depois de medidos.

---

## BLOCO 4 — Provider real

Objetivo:

Integrar **um** provider LLM pelas boundaries existentes.

Requisitos:

- configuração por ambiente;
- secret fora do Git;
- timeout;
- failure mapping;
- mocks/fakes nos testes;
- execução real controlada.

Não integrar múltiplos providers apenas para aumentar a stack.

---

## BLOCO 5 — RAG real fundamentado

Objetivo:

Executar semantic answerability e geração reais.

Entregáveis:

- semantic answerability real;
- generation real;
- abstention real;
- answer + sources;
- prompt documentado;
- limitações registradas.

Regras:

```text
retrieval success
≠
answerability
```

```text
source provided
≠
claim-level proof
```

Na V1, sources representam provenance do contexto.

---

## BLOCO 6 — Operação e observabilidade

Objetivo:

Inspecionar o comportamento operacional.

Medir:

- requests;
- sucessos;
- erros;
- tipos de erro;
- latência;
- p50;
- p95;
- abstention rate;
- provider calls;
- provider failures.

Logs não devem expor:

- API keys;
- passwords;
- JWT;
- secrets.

Não definir SLO rígido de latência antes de medir baseline real.

---

## BLOCO 7 — CI/CD e deploy

Objetivo:

Tornar o sistema reproduzível fora da máquina de desenvolvimento.

Entregáveis:

- CI;
- deploy demonstrável;
- migrations controladas;
- health/smoke test;
- `.env.example`;
- documentação de setup;
- secrets externos.

O avaliador deve poder executar usando suas próprias credenciais.

---

## BLOCO 8 — Fechamento da V1

Objetivo:

Congelar uma versão tecnicamente defensável.

Entregáveis:

- README final;
- arquitetura;
- ADRs;
- evaluation report;
- métricas reais;
- limitações;
- reprodução local;
- roteiro de entrevista;
- aula gravada;
- vídeo final de portfólio;
- release/tag V1.

---

# 5. Distribuição do esforço restante

Meta estratégica:

| Área | Peso |
|---|---:|
| RAG real + evaluation | 40% |
| Segurança operacional + confiabilidade + observabilidade | 25% |
| CI/CD + deploy + reprodutibilidade | 20% |
| Documentação + explicação + apresentação | 15% |

Total:

**100%**

São pesos de prioridade futura.

Não são estatísticas das horas históricas do projeto.

---

# 6. Gates da V1

## Testes

Suíte automatizada:

**100% verde**

---

## Segurança

Casos cross-user controlados:

**100% devem passar**

Qualquer vazamento observado bloqueia a V1.

Isso não significa afirmar "100% seguro em produção".

---

## Evaluation

Obrigatório:

- dataset versionado;
- métricas reproduzíveis;
- resultados registrados;
- limitações registradas.

---

## Entrega

Obrigatório:

- CI verde;
- deploy demonstrável;
- setup reproduzível;
- secrets externos;
- documentação de execução.

---

## Explicação

Cícero deve conseguir explicar:

1. autenticação vs autorização;
2. ownership;
3. filtro antes de ranking/top_k;
4. migrations;
5. textual vs semantic vs hybrid retrieval;
6. RRF;
7. Context Builder;
8. retrieval vs answerability;
9. abstention vs provider failure;
10. provenance vs claim-level grounding;
11. limitações da V1.

---

# 7. Portfolio & Demonstration Layer

Decisão:

**live demo pública com LLM pago não é requisito**

Formato padrão:

- GitHub;
- README;
- case study visual;
- arquitetura;
- evaluation report;
- métricas reais;
- exemplos de execução;
- demonstração gravada;
- reprodução local;
- página estática opcional.

---

## Vídeo final

Duração proposta:

**5–8 minutos**

Conteúdo:

1. problema;
2. arquitetura;
3. banco e ownership;
4. retrieval;
5. pergunta respondível;
6. sources;
7. abstention;
8. cross-user isolation;
9. provider failure;
10. testes;
11. métricas;
12. limitações.

Pode ser publicado como vídeo não listado.

---

# 8. Dados

Separar:

### Evaluation dataset

Criado para medir comportamento.

### Demo dataset

Pequeno, controlado e publicável.

### Dados privados/reais

Não entram no repositório público.

Conteúdo próprio pode futuramente ser usado como demonstração quando houver:

- direito de publicação;
- utilidade concreta;
- justificativa de escopo.

---

# 9. Regra contra projeto infinito

Antes de incluir uma nova feature:

```text
qual problema concreto isso resolve?
```

Depois:

```text
como vamos medir se resolveu?
```

Sem resposta convincente, não entra.

Depois da V1, mudança só deve ser priorizada quando:

1. evaluation revelar problema;
2. entrevistas/vagas mostrarem gap recorrente;
3. uso real mostrar necessidade.

---

# 10. Política de revisão

| Horizonte | Revisão |
|---|---|
| Curto prazo | semanal |
| Médio prazo | mensal |
| Longo prazo | trimestral |

Uma biblioteca nova não muda a estratégia.

Uma vaga isolada não muda a stack.

Evidência recorrente pode alterar prioridade.

---

# 11. Método de aprendizagem

Fluxo:

```text
CONSTRUIR
→ PROVAR
→ EXPLICAR
→ REVISAR
```

Continuam fazendo parte do método:

- prática;
- testes;
- documentação;
- NotebookLM;
- diário técnico;
- revisão;
- simulação de entrevista;
- mercado;
- aula gravada semanal de aproximadamente 20 minutos.

---

# 12. Definição de sucesso

O objetivo não é construir o maior projeto possível.

O objetivo é conseguir afirmar e demonstrar:

> Construí um backend real, tomei decisões arquiteturais justificadas, implementei isolamento de dados, testei o comportamento, medi qualidade, integrei IA de forma controlada, documentei limitações e consigo explicar o sistema.

---

# 13. Trabalho atual

Bloco:

**BLOCO 1 — VALIDAÇÃO CONTROLADA DO PIPELINE RAG**

Branch:

`rag-block-01-controlled-validation`

Próxima ação:

```text
inspecionar cobertura RAG existente
↓
mapear os cinco comportamentos
↓
identificar gaps
↓
implementar somente o que falta
↓
validar
↓
documentar
```

Provider real só entra depois desse gate.
