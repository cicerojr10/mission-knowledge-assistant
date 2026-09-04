# RAG BLOCK 02 — EVALUATION HARNESS

**Status:** em finalização

**Objetivo:** construir uma avaliação reproduzível baseada em dataset versionado, separando testes de software de avaliação de qualidade.

---

## 1. Problema

A suíte automatizada do MKA verificava contratos e regressões do software, mas não respondia diretamente perguntas de qualidade como:

- o retrieval encontra a evidência esperada?
- em qual posição ela aparece?
- evidência pertencente a outro usuário aparece no ranking?
- uma mudança futura melhora ou piora o comportamento?
- o experimento pode ser reproduzido sobre dados fixos?

A distinção adotada é:

```text
pytest
→ contratos e regressões do software

evaluation
→ comportamento medido sobre casos fixos
```

---

## 2. Arquitetura da evaluation

A evaluation foi mantida fora do runtime principal.

```text
evaluation/
├── __init__.py
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

Responsabilidades:

```text
app/
→ runtime da aplicação

tests/
→ contratos e regressões

evaluation/
→ experimentos de qualidade reproduzíveis
```

Nenhuma biblioteca externa específica de evaluation foi adicionada neste bloco.

---

## 3. Dataset versionado

Cada `EvaluationCase` possui atualmente:

```text
id
category
owner_key
question
expected_abstained
expected_document_keys
forbidden_document_keys
reference_answer
```

Categorias:

- `answerable`;
- `unanswerable`;
- `cross_user`;
- `difficult`.

O dataset não depende de IDs gerados pelo PostgreSQL.

São utilizadas chaves estáveis como:

```text
security-ownership
database-migrations
rag-abstention
private-secondary
```

Durante a execução:

```text
document_key
↓
Document persistido
↓
document_id gerado
↓
mapeamento document_id → document_key
```

---

## 4. Ownership

O corpus e os casos possuem `owner_key`.

Isso permite representar explicitamente:

```text
quem possui o documento
+
quem executa a consulta
```

Exemplo cross-user:

```text
private-secondary
→ owner_key = secondary

eval-006
→ owner_key = primary
```

Assim o isolamento não depende de uma convenção implícita.

---

## 5. Corpus piloto

O corpus piloto possui 4 documentos.

Usuário `primary`:

- `security-ownership`;
- `database-migrations`;
- `rag-abstention`.

Usuário `secondary`:

- `private-secondary`.

Os documentos são pequenos para reduzir variáveis nesta primeira validação.

Com o chunker atual:

```text
chunk_size = 500
overlap = 50
```

cada documento piloto gera um único chunk.

---

## 6. Casos piloto

O dataset atual possui 8 casos.

| Categoria | Casos |
|---|---:|
| Answerable | 3 |
| Unanswerable | 2 |
| Cross-user | 2 |
| Difficult | 1 |
| Total | 8 |

Esse conjunto é um piloto.

O plano mestre propõe expansão para aproximadamente 50 casos.

Portanto:

```text
8 casos
≠
dataset final planejado
```

---

## 7. Runner

O runner foi desacoplado da aplicação.

```text
EvaluationCase
↓
executor
↓
EvaluationObservation
↓
EvaluationResult
↓
summary
```

Isso permite usar executores diferentes sem alterar o contrato principal da evaluation.

O harness controlado verifica inicialmente:

- correspondência de abstention;
- presença de documentos esperados;
- ausência de documentos proibidos.

O `reference_answer` ainda não é usado para medir qualidade de geração.

---

## 8. Métricas do harness

A infraestrutura calcula:

- total de casos;
- casos aprovados;
- pass rate;
- abstention match rate;
- expected documents found rate;
- forbidden documents absent rate.

Também existe segmentação por categoria.

O objetivo é evitar que uma média global esconda uma categoria fraca.

---

## 9. Harness controlado

Antes de executar retrieval real, o pipeline foi validado com um executor controlado.

Esse executor devolve propositalmente os resultados esperados.

Portanto, resultados de 100% nessa etapa demonstram apenas que:

```text
dataset
→ runner
→ result
→ metrics
```

funcionam de forma consistente.

Eles não representam qualidade observada do retrieval.

---

## 10. Executor de retrieval real

Foi criado um executor específico para retrieval.

Ele não utiliza `abstained`, porque retrieval não decide answerability.

Responsabilidades:

1. criar usuários temporários de evaluation;
2. persistir documentos;
3. aplicar o chunker real;
4. gerar embeddings;
5. persistir vetores;
6. executar `search_chunks_hybrid()`;
7. mapear IDs do banco para `document_key`;
8. preservar ranking;
9. remover os dados temporários.

A busca recebe `owner_id` real.

Isso mede retrieval sem adicionar autenticação HTTP como variável do experimento.

---

## 11. Embeddings

A execução observada utilizou o serviço real existente:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Dimensão:

```text
384
```

Os vetores foram armazenados no PostgreSQL com pgvector.

Nenhum novo modelo foi introduzido apenas para melhorar o resultado da evaluation.

---

## 12. Pytest vs quality evaluation

O carregamento real do SentenceTransformer não faz parte do requisito normal dos testes unitários do executor.

Nos testes:

- hashing pode ser controlado;
- embeddings podem ser controlados;
- retrieval pode ser substituído.

Na avaliação real:

- PostgreSQL é real;
- pgvector é real;
- embeddings são reais;
- busca híbrida é real.

Isso mantém a separação:

```text
pytest
→ rápido e determinístico

quality evaluation
→ execução experimental explícita
```

---

## 13. Comando reproduzível

A primeira medição real foi executada com:

```text
python -m evaluation.run_retrieval --top-k 1
```

Configuração:

```text
top_k = 1
max_distance = None
```

`top_k=1` foi escolhido porque o corpus piloto possui somente três documentos autorizados para o usuário `primary`.

Com esse corpus reduzido, `Recall@5` teria pouco poder discriminativo.

---

## 14. Primeira medição observada

Configuração do experimento:

| Item | Valor |
|---|---|
| Documentos | 4 |
| Casos | 8 |
| Casos pontuados | 6 |
| `top_k` | 1 |
| `max_distance` | `None` |
| Embedding | `all-MiniLM-L6-v2` |
| Dimensão | 384 |
| Banco | PostgreSQL |
| Busca vetorial | pgvector |
| Retrieval | hybrid + RRF |

Resultados observados:

| Métrica | Resultado |
|---|---:|
| Scored pass rate | 100% |
| Expected case hit@1 | 100% |
| Expected document recall@1 | 100% |
| Forbidden document absence | 100% |

Esses números pertencem somente ao experimento piloto descrito acima.

---

## 15. Resultados por caso

### eval-001 — answerable

```text
retrieved = security-ownership
first_expected_rank = 1
```

### eval-002 — answerable

```text
retrieved = database-migrations
first_expected_rank = 1
```

### eval-003 — answerable

```text
retrieved = rag-abstention
first_expected_rank = 1
```

### eval-004 — unanswerable

```text
retrieved = database-migrations
status = INFO
```

### eval-005 — unanswerable

```text
retrieved = database-migrations
status = INFO
```

### eval-006 — cross_user

```text
retrieved = security-ownership
private-secondary = absent
```

### eval-007 — cross_user

```text
retrieved = security-ownership
private-secondary = absent
```

### eval-008 — difficult

```text
retrieved = rag-abstention
first_expected_rank = 1
```

---

## 16. Achado sobre perguntas unanswerable

Os casos `eval-004` e `eval-005` retornaram `database-migrations` como vizinho mais próximo.

Isso não foi tratado como falha de abstention.

A camada de retrieval responde:

```text
qual evidência autorizada é mais próxima?
```

A camada de answerability responde:

```text
essa evidência é suficiente para responder?
```

Portanto:

```text
retrieval success
≠
answerability
```

A observação experimental reforça a necessidade de manter as duas responsabilidades separadas.

---

## 17. Cross-user

Nos casos `eval-006` e `eval-007`, o documento proibido:

```text
private-secondary
```

pertencia ao usuário `secondary`.

A consulta foi executada usando o `owner_id` correspondente ao usuário `primary`.

O documento proibido não apareceu em nenhum dos dois resultados.

Resultado observado:

```text
forbidden_document_absence = 100%
```

Isso é evidência positiva nos casos controlados executados.

Não é prova de segurança de produção.

---

## 18. Cleanup

Após a execução real foi verificado:

```text
evaluation_users_remaining=0
```

Isso confirma que os usuários temporários da execução observada foram removidos.

O executor remove apenas os registros associados ao corpus criado pela própria evaluation.

---

## 19. Estado dos testes

Após a implementação do comando e das métricas específicas de retrieval:

```text
145 passed
2 warnings
```

Warnings conhecidos:

1. Starlette TestClient/httpx;
2. `HTTP_413_REQUEST_ENTITY_TOO_LARGE`.

Esses warnings já existiam e não foram introduzidos pelo Evaluation Harness.

---

## 20. Limitações

### Corpus reduzido

Existem somente 4 documentos.

### Dataset reduzido

Existem somente 8 casos.

### Retrieval esperado

Somente 4 casos possuem documento esperado para medição direta.

### Cross-user

Existem somente 2 casos cross-user.

### Unanswerable

Os dois casos unanswerable são informativos na avaliação de retrieval.

Eles não medem abstention real.

### Idioma

O piloto atual está em inglês.

Ainda não existe avaliação formal em português ou cross-language.

### Generation

Nenhum provider LLM real foi avaliado neste bloco.

### Groundedness

Groundedness ainda não foi medido.

### Sources

Sources continuam representando provenance do contexto.

Não existe claim-level validation.

---

## 21. Interpretação correta

É correto afirmar:

> No corpus piloto de 4 documentos e 8 casos, usando `top_k=1`, PostgreSQL, pgvector, embeddings reais do `all-MiniLM-L6-v2` e hybrid retrieval real, todos os casos pontuados atenderam aos critérios definidos para recuperação esperada e isolamento cross-user.

Não afirmar:

- retrieval possui 100% de qualidade geral;
- RAG possui 100% de precisão;
- segurança foi comprovada em produção;
- o sistema está production-ready;
- o experimento representa uso real amplo.

---

## 22. Status do Bloco 2

Concluído até aqui:

- modelos de evaluation;
- corpus loader;
- dataset loader;
- dataset versionado;
- corpus piloto;
- 8 casos piloto;
- runner;
- métricas gerais;
- segmentação por categoria;
- executor de retrieval;
- métricas específicas de retrieval;
- comando reproduzível;
- PostgreSQL real;
- pgvector real;
- embeddings reais;
- hybrid search real;
- primeira medição observada;
- cleanup validado.

Pendente para fechar completamente o Bloco 2:

- expandir o dataset em direção aos 50 casos propostos;
- consolidar cobertura por categoria;
- executar novamente a evaluation sobre o conjunto ampliado;
- registrar a medição ampliada;
- atualizar o estado oficial do projeto.

---

## 23. Próximo passo

Expandir o dataset de forma controlada.

Meta proposta no plano mestre:

```text
50 casos
```

Cobertura planejada:

| Categoria | Meta |
|---|---:|
| Answerable | 40% |
| Unanswerable / abstention | 25% |
| Cross-user / security | 20% |
| Difíceis / ambíguos / ruidosos | 15% |

Esses percentuais representam desenho experimental.

Não são resultados observados.

Depois da expansão, o mesmo executor deverá produzir uma nova medição antes de o Bloco 2 ser considerado concluído.
