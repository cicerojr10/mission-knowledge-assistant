# Semana 03 - Check-in técnico

## Tema

Chunking e busca textual.

## Objetivo da semana

Transformar documentos persistidos em chunks consultáveis e implementar busca textual inicial sobre esses chunks.

## Entregas concluídas

- [x] Criado model `Chunk`
- [x] Configurada relação `Document 1:N Chunk`
- [x] Criada migration Alembic para tabela `chunks`
- [x] Aplicada migration no PostgreSQL
- [x] Criada função `split_text()`
- [x] Configurado chunking com `chunk_size=500` e `overlap=50`
- [x] Criados testes unitários para o chunker
- [x] Integrado chunking ao `POST /documents`
- [x] Persistidos chunks na mesma transação do documento
- [x] Adicionado campo `chunk_count` em `DocumentResponse`
- [x] Criado endpoint `GET /documents/{document_id}/chunks`
- [x] Criado endpoint `GET /search?q=termo`
- [x] Implementada busca textual com `ILIKE`
- [x] Criados testes de integração para documentos, chunks e busca
- [x] Criado `ADR-003-chunks-table.md`
- [x] Criado `ADR-004-chunking-strategy.md`
- [x] Criado `ADR-005-text-search-ilike.md`
- [x] Atualizado `README.md`
- [x] Criado `docs/semana-03-guia.md`

## Validações executadas

| Validação | Comando | Resultado |
|---|---|---|
| Testes do chunker | `pytest tests\test_chunker.py` | `11 passed` |
| Testes de documentos | `pytest tests\test_documents.py` | `7 passed` |
| Testes de busca | `pytest tests\test_search.py` | `4 passed` |
| Suíte completa | `pytest` | `23 passed` |

## Decisões registradas

| ADR | Decisão |
|---|---|
| ADR-003 | Modelar chunks em tabela separada |
| ADR-004 | Usar chunking inicial por tamanho fixo com overlap |
| ADR-005 | Usar `ILIKE` como busca textual inicial |

## Estado técnico ao final da semana

- FastAPI
- PostgreSQL
- SQLModel
- Alembic
- `Document 1:N Chunk`
- Chunking com overlap
- Persistência de chunks
- Busca textual com `ILIKE`
- Testes automatizados
- ADRs atualizadas
- README atualizado

## Fora de escopo mantido

- [x] Embeddings não implementados
- [x] pgvector não implementado
- [x] Busca vetorial não implementada
- [x] RAG não implementado
- [x] LLM não integrado
- [x] Repository pattern não introduzido
- [x] Async não introduzido

## Critério de conclusão

A Semana 3 está concluída quando:

- [x] O documento é salvo no PostgreSQL
- [x] O documento gera chunks automaticamente
- [x] Os chunks são persistidos no banco
- [x] Os chunks podem ser listados por documento
- [x] A busca textual retorna chunks compatíveis com o termo pesquisado
- [x] A suíte completa passa com `pytest`
- [x] As decisões técnicas estão registradas em ADRs
- [x] O README descreve o estado atual do projeto