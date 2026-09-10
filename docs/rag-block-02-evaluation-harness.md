# RAG BLOCK 02 — EVALUATION HARNESS

**Status:** concluído

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

## 3. Contrato do dataset

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

São utilizadas chaves lógicas e estáveis como:

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

consulta cross-user
→ owner_key = primary
```

Assim o isolamento não depende de uma convenção implícita.

---

## 5. Evolução do corpus

### Piloto

O primeiro corpus possuía 4 documentos:

Usuário `primary`:

- `security-ownership`;
- `database-migrations`;
- `rag-abstention`.

Usuário `secondary`:

- `private-secondary`.

Esse corpus pequeno serviu para validar a infraestrutura e a primeira execução real.

### Corpus ampliado

O benchmark ampliado possui:

```text
18 documentos
```

Ele inclui documentos relacionados a:

- ownership;
- autenticação JWT;
- password hashing;
- migrations;
- chunking;
- semantic retrieval;
- hybrid retrieval;
- Context Builder;
- answerability/abstention;
- generation gate;
- provider failures;
- sources/provenance;
- evaluation;
- documentos privados do usuário `secondary`.

Os documentos foram mantidos abaixo do `chunk_size=500` nesta etapa.

Isso foi deliberado: o benchmark aumentou a competição entre documentos sem introduzir ainda a variável de múltiplos chunks por documento.

---

## 6. Evolução do dataset

### Piloto

O primeiro dataset possuía 8 casos:

| Categoria | Casos |
|---|---:|
| Answerable | 3 |
| Unanswerable | 2 |
| Cross-user | 2 |
| Difficult | 1 |
| Total | 8 |

### Dataset ampliado

O dataset atual possui 50 casos:

| Categoria | Casos | Proporção |
|---|---:|---:|
| Answerable | 20 | 40% |
| Unanswerable | 13 | 26% |
| Cross-user | 10 | 20% |
| Difficult | 7 | 14% |
| **Total** | **50** | **100%** |

A distribuição aproxima a meta de desenho experimental do plano mestre:

```text
40% answerable
25% unanswerable / abstention
20% cross-user / security
15% difficult / ambiguous / noisy
```

Os percentuais são desenho do dataset, não resultados do sistema.

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

Isso permite substituir o executor sem alterar o contrato principal da evaluation.

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

Isso evita esconder uma categoria fraca dentro de uma média global.

---

## 9. Harness controlado

Antes de executar retrieval real, o pipeline foi validado com um executor controlado.

Esse executor devolve propositalmente os resultados esperados.

Portanto, resultados de 100% no harness controlado demonstram apenas que:

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
9. remover os dados temporários criados pela execução.

A busca recebe `owner_id` real.

Isso mede retrieval sem adicionar autenticação HTTP como variável do experimento.

---

## 11. Embeddings e banco

A execução observada utilizou:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Dimensão:

```text
384
```

Infraestrutura real utilizada:

- PostgreSQL;
- pgvector;
- embeddings reais;
- hybrid retrieval real;
- Reciprocal Rank Fusion.

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

Separação:

```text
pytest
→ rápido e determinístico

quality evaluation
→ execução experimental explícita
```

Após a expansão do dataset:

```text
23 testes específicos de evaluation passaram
147 testes totais passaram
2 warnings conhecidos
```

---

## 13. Comandos reproduzíveis

Hit@1:

```text
python -m evaluation.run_retrieval --top-k 1
```

Recall@5:

```text
python -m evaluation.run_retrieval --top-k 5
```

Configuração comum:

```text
max_distance = None
```

Com 18 documentos, a comparação entre `top_k=1` e `top_k=5` passa a ser informativa.

---

## 14. Primeira medição — piloto

A primeira execução real, ainda sobre 4 documentos e 8 casos, produziu:

| Métrica | Resultado |
|---|---:|
| Scored pass rate | 100% |
| Expected case hit@1 | 100% |
| Expected document recall@1 | 100% |
| Forbidden document absence | 100% |

Esse resultado serviu para validar o fluxo experimental.

Ele não foi tratado como benchmark amplo por causa do corpus muito pequeno.

---

## 15. Benchmark ampliado — top_k=1

Configuração:

| Item | Valor |
|---|---|
| Documentos | 18 |
| Casos | 50 |
| Casos pontuados | 37 |
| Casos com documento esperado | 27 |
| Casos cross-user | 10 |
| Casos unanswerable | 13 |
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
| Scored pass rate | 94.59% |
| Expected case hit@1 | 92.59% |
| Expected document recall@1 | 92.59% |
| Forbidden document absence | 100.00% |

Em números absolutos:

```text
25 de 27 casos com documento esperado
→ documento esperado em rank 1

10 de 10 casos cross-user
→ documento proibido ausente

13 casos unanswerable
→ informativos para retrieval
```

---

## 16. Falhas observadas em rank 1

Dois casos não recuperaram o documento esperado em primeiro lugar.

### eval-003

Pergunta relacionada a evidência insuficiente e abstention.

Esperado:

```text
rag-abstention
```

Rank 1 observado:

```text
sources-provenance
```

### eval-008

Pergunta sobre contexto relacionado não autorizar automaticamente geração.

Esperado:

```text
rag-abstention
```

Rank 1 observado:

```text
sources-provenance
```

Os dois resultados mostraram competição semântica entre documentos próximos do mesmo pipeline RAG.

---

## 17. Benchmark ampliado — top_k=5

A mesma evaluation foi executada sem alterar corpus, casos ou algoritmo, mudando apenas:

```text
top_k = 5
```

Resultados:

| Métrica | Resultado |
|---|---:|
| Scored pass rate | 100.00% |
| Expected case hit@5 | 100.00% |
| Expected document recall@5 | 100.00% |
| Forbidden document absence | 100.00% |

Nos dois casos que falharam em rank 1:

```text
eval-003
rag-abstention → rank 2

eval-008
rag-abstention → rank 3
```

Portanto, o documento esperado não estava ausente.

Ele estava abaixo de outro documento semanticamente relacionado.

---

## 18. Diagnóstico de retrieval

A comparação entre `@1` e `@5` indica:

```text
não é principalmente:
falha de recall

é principalmente:
competição de ranking entre documentos semanticamente próximos
```

Resumo:

| Métrica | top_k=1 | top_k=5 |
|---|---:|---:|
| Expected document hit | 92.59% | 100.00% |
| Expected document recall | 92.59% | 100.00% |
| Forbidden document absence | 100.00% | 100.00% |

Esse diagnóstico é mais útil do que ajustar o benchmark apenas para obter 100% em rank 1.

Nenhum tuning foi feito depois da medição para esconder as duas falhas.

---

## 19. Unanswerable e cross-user

### Unanswerable

Os 13 casos unanswerable retornam vizinhos autorizados porque retrieval procura candidatos semanticamente próximos.

Isso não significa que a pergunta seja respondível.

```text
retrieval
→ encontra candidatos autorizados

answerability
→ decide se a evidência é suficiente

abstention
→ ocorre quando geração não deve ser autorizada
```

Assim:

```text
retrieval success
≠
answerability
```

### Cross-user

Foram executados 10 casos cross-user.

Resultado observado:

```text
forbidden_document_absence = 100%
```

Nenhum documento proibido do usuário `secondary` apareceu nos resultados desses 10 casos.

Isso é evidência positiva dentro do experimento controlado.

Não é prova de segurança de produção.

---

## 20. Limitações

### Corpus controlado

O benchmark possui 18 documentos criados especificamente para evaluation.

Não representa uma base documental ampla de produção.

### Documentos de um único chunk

Os documentos foram mantidos abaixo de 500 caracteres.

Portanto, esta etapa não mede competição entre múltiplos chunks do mesmo documento.

### Dataset controlado

Os 50 casos são versionados e úteis para regressão, mas continuam sendo um benchmark controlado.

### Idioma

O dataset atual está em inglês.

Ainda não existe avaliação formal separada para português ou cross-language.

### Unanswerable

Os casos unanswerable são informativos na camada de retrieval.

Eles não medem o comportamento real do semantic answerability evaluator.

### Generation

Nenhum provider LLM real foi avaliado neste bloco.

### Groundedness

Groundedness ainda não foi medido.

### Sources

Sources continuam representando provenance do contexto.

Não existe claim-level validation.

### Latência

Não foi produzido benchmark formal de latência nesta etapa.

### Produção

Os resultados não demonstram performance, segurança ou confiabilidade de produção.

---

## 21. Interpretação correta

Pode ser afirmado:

> Em um benchmark controlado e versionado com 18 documentos e 50 casos, o hybrid retrieval do MKA recuperou o documento esperado em rank 1 em 25 de 27 casos avaliáveis, equivalente a 92,59% de Hit@1/Recall@1. Com top_k=5, os 27 casos continham a evidência esperada, resultando em 100% de Hit@5/Recall@5. Nos 10 casos cross-user, nenhum documento proibido apareceu nos resultados.

Também pode ser afirmado:

> As duas falhas de rank 1 foram casos de competição de ranking: a evidência esperada apareceu nas posições 2 e 3.

Não afirmar:

- retrieval possui 100% de qualidade geral;
- RAG possui 100% de precisão;
- segurança foi comprovada em produção;
- o sistema está production-ready;
- o benchmark representa uso real amplo;
- groundedness ou geração foram avaliados neste bloco.

---

## 22. Status do Bloco 2

Status:

```text
CONCLUÍDO
```

Entregas:

- modelos de evaluation;
- corpus loader;
- dataset loader;
- dataset versionado;
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
- corpus ampliado para 18 documentos;
- dataset ampliado para 50 casos;
- 20 casos answerable;
- 13 casos unanswerable;
- 10 casos cross-user;
- 7 casos difficult;
- benchmark `top_k=1`;
- benchmark `top_k=5`;
- diagnóstico de ranking;
- 147 testes passando;
- limitações registradas.

Nenhuma alteração do algoritmo de retrieval foi feita para otimizar os resultados depois de observar o benchmark.

---

## 23. Próximo bloco

### BLOCO 3 — Retrieval vs Generation Evaluation

Objetivo:

Separar falhas por camada do pipeline.

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

O próximo bloco deve distinguir, de forma mensurável:

- documento correto não recuperado;
- contexto recuperado, mas insuficiente;
- decisão de answerability incorreta;
- geração não fundamentada;
- abstention correta;
- provider failure;
- sources/provenance.

O Bloco 2 encerra a infraestrutura e a baseline de retrieval.

Ele não encerra a evaluation completa do RAG.
