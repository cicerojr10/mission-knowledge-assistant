# ADR-002 - Persistência com PostgreSQL, SQLModel e Alembic

## Status

Aceita

## Contexto

O projeto iniciou com armazenamento de documentos em memória usando uma lista Python. Essa abordagem foi suficiente para validar os primeiros endpoints da API, mas não atende ao requisito de persistência real.

Com armazenamento em memória, os documentos são perdidos quando a aplicação é reiniciada. Para evoluir a API para uma base adequada a um assistente de conhecimento baseado em documentos, é necessário persistir dados em um banco relacional, manter informações após reinícios e versionar a estrutura do banco.

A Semana 2 teve como objetivo migrar a persistência de documentos para PostgreSQL real, executado via Docker Compose, com schema controlado por migrations.

## Decisão

Utilizar PostgreSQL 16 como banco de dados relacional, executado via Docker Compose com volume nomeado `postgres_data`.

Utilizar SQLModel como camada de modelagem e acesso ao banco, mantendo conexão síncrona.

Utilizar Alembic para versionar alterações de schema, começando pela criação da tabela `document`.

## Motivos

* PostgreSQL é um banco relacional robusto e amplamente usado em aplicações backend.
* SQLModel oferece uma forma simples de declarar modelos com tipagem Python e integração com SQLAlchemy.
* A abordagem síncrona reduz complexidade neste estágio do projeto.
* Docker Compose facilita subir o banco localmente de forma reproduzível.
* O volume nomeado `postgres_data` preserva os dados quando o container é removido sem apagar volumes.
* Alembic permite versionar a estrutura do banco e recriar o schema em ambientes novos.
* Essa base prepara o projeto para evoluções futuras, como chunks, embeddings e pgvector.

## Alternativas consideradas

### Manter armazenamento em memória

Rejeitada porque os dados são perdidos ao reiniciar a aplicação e a abordagem não representa um cenário real de backend.

### Usar SQLite

Rejeitada porque o objetivo da semana era trabalhar com PostgreSQL real, mais próximo de ambientes profissionais e compatível com evolução futura para `pgvector`.

### Usar SQLAlchemy puro

Rejeitada neste momento para reduzir complexidade. SQLModel atende ao objetivo atual com menos boilerplate e boa integração com type hints.

### Criar tabelas com `SQLModel.metadata.create_all`

Rejeitada como estratégia principal porque não versiona mudanças de schema. O projeto adotou Alembic para migrations controladas.

### Usar driver assíncrono

Rejeitada porque a stack da semana definiu conexão síncrona. Async será avaliado apenas se houver necessidade futura.

## Consequências

A API passa a persistir documentos em PostgreSQL em vez de memória.

As rotas que acessam dados persistidos dependem de uma sessão de banco fornecida por `get_session()`.

A criação e evolução das tabelas passam a ser controladas por migrations Alembic.

O ambiente local exige PostgreSQL rodando via Docker Compose antes de executar rotas ou testes que acessam o banco.

Os testes automatizados que acessam persistência precisam limpar dados entre execuções para evitar dependência de estado persistido.

Decisões posteriores expandiram essa base com a tabela `chunks` e com o relacionamento `Document -> Chunk`, mantendo PostgreSQL, SQLModel e Alembic como fundação de persistência.

## Validação

Foi validado o ciclo de recriação do banco do zero:

```text
docker compose down -v
docker compose up -d
alembic upgrade head
pytest
```

Resultado esperado no estado atual do projeto:

```text
23 passed
```
