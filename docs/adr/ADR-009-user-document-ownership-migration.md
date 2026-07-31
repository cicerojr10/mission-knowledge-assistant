# ADR-009 - Migração incremental para ownership de documentos

## Status

Aceita

## Contexto

O Mission Knowledge Assistant foi inicialmente desenvolvido como uma aplicação de usuário único.

Os documentos e seus chunks eram armazenados globalmente, sem uma identidade associada ao proprietário do conteúdo.

A estrutura era:

User inexistente

Document
→ Chunk

Essa modelagem era suficiente para as primeiras etapas de persistência, chunking e retrieval, mas não oferece isolamento entre usuários.

Com a evolução do projeto para autenticação, autorização e RAG, tornou-se necessário identificar o proprietário de cada documento.

Sem ownership, um usuário poderia acessar conteúdo de outra conta diretamente por identificador ou indiretamente pelos mecanismos de retrieval:

- busca textual;
- busca semântica;
- busca híbrida;
- futuro contexto enviado ao LLM.

Esse risco é especialmente importante porque um vazamento no retrieval poderia fazer o modelo gerar uma resposta utilizando chunks pertencentes a outro usuário.

## Decisão

Introduzir o modelo `User` e o relacionamento:

User
→ Document
→ Chunk

O proprietário será armazenado em:

`Document.owner_id`

O modelo `Chunk` não receberá um campo de proprietário duplicado.

O dono de um chunk será determinado por:

Chunk
→ Document
→ User

Essa decisão evita duplicação de ownership e mantém `Document` como a fronteira de autorização do conteúdo.

## Estratégia de migração

A alteração será realizada utilizando a estratégia:

Expand
→ Backfill
→ Enforce

### Expand

Nesta primeira fase foram adicionados:

- tabela `users`;
- coluna `document.owner_id`;
- índice em `document.owner_id`;
- foreign key de `document.owner_id` para `users.id`;
- relacionamento ORM entre `User` e `Document`.

Durante esta fase, `owner_id` permanece temporariamente nullable.

Isso preserva compatibilidade com o comportamento e com os testes existentes enquanto autenticação e autorização ainda estão sendo introduzidas.

### Backfill

Na segunda fase, a aplicação passará a criar documentos utilizando a identidade autenticada.

O proprietário não será enviado pelo cliente no schema `DocumentCreate`.

O valor será obtido internamente a partir do usuário autenticado:

JWT
→ current_user
→ current_user.id
→ Document.owner_id

Os testes existentes também serão adaptados para criar usuários e documentos com ownership explícito.

Como o banco de desenvolvimento estava vazio no momento desta migration, não foi necessário criar um usuário legado nem migrar documentos existentes.

### Enforce

Depois que todas as rotas, serviços e testes produzirem documentos com proprietário, uma nova migration tornará:

`document.owner_id NOT NULL`

Nesse estágio, o próprio PostgreSQL impedirá a existência de documentos sem proprietário.

O estado nullable atual é transitório e não representa o estado final de segurança.

## Autorização

A existência de `owner_id` não implementa autorização por si só.

As operações futuras deverão comparar o usuário autenticado com o proprietário do recurso.

Conceitualmente:

`Document.owner_id == current_user.id`

Essa regra deverá ser aplicada tanto ao acesso direto a documentos quanto aos serviços de retrieval.

Todos os mecanismos deverão filtrar resultados pelo proprietário:

- listagem de documentos;
- acesso a documento por identificador;
- listagem de chunks;
- busca textual;
- busca semântica;
- busca híbrida;
- futuro pipeline de RAG.

## Propriedade definida pelo servidor

O campo `owner_id` não fará parte de `DocumentCreate`.

O cliente não poderá escolher diretamente o proprietário do documento.

A propriedade será definida pelo servidor a partir da identidade autenticada.

Isso evita que uma requisição tente criar um documento em nome de outro usuário manipulando o payload.

## Password hash

O modelo `User` possui o campo:

`password_hash`

A aplicação não pretende persistir senhas em texto puro.

Nesta primeira fase, os testes utilizam valores fictícios porque password hashing e cadastro ainda não foram implementados.

Uma etapa posterior introduzirá hashing de senha com uma biblioteca apropriada.

## Alternativas consideradas

### Tornar owner_id obrigatório imediatamente

Rejeitado nesta fase.

Isso quebraria simultaneamente os testes e os fluxos existentes, antes que autenticação e criação de usuários estivessem disponíveis.

A mudança dificultaria identificar regressões e misturaria modelagem, autenticação, autorização e retrieval em uma única alteração.

### Adicionar user_id também em Chunk

Rejeitado.

O proprietário já pode ser determinado através do relacionamento com `Document`.

Duplicar o campo aumentaria o risco de inconsistência entre:

- `Chunk.user_id`;
- `Chunk.document_id`;
- `Document.owner_id`.

### Permitir owner_id no payload de criação

Rejeitado.

A propriedade do recurso deve ser derivada da identidade autenticada e não de um valor controlado pelo cliente.

### Implementar JWT antes do ownership

Rejeitado.

JWT identifica a requisição, mas não define sozinho quais objetos o usuário pode acessar.

A fronteira de ownership precisa existir para que a autorização possa ser aplicada corretamente.

## Trade-offs

A estratégia incremental permite manter o sistema funcional durante a transição.

Em contrapartida, existe temporariamente a possibilidade técnica de persistir um documento com `owner_id` nulo.

Esse estado será eliminado na fase Enforce.

Até essa fase ser concluída, o projeto ainda não deve ser descrito como possuindo isolamento completo entre usuários.

## Consequências

O projeto passa a possuir a fundação necessária para:

- cadastro de usuários;
- password hashing;
- autenticação;
- JWT;
- resolução de `current_user`;
- autorização por objeto;
- isolamento dos mecanismos de retrieval;
- RAG fundamentado apenas em documentos autorizados.

A introdução do modelo `User` não significa que autenticação já esteja implementada.

Ela estabelece somente a estrutura de dados necessária para as próximas etapas.

## Validação

A migration `48f6808a4554` criou:

- tabela `users`;
- coluna nullable `document.owner_id`;
- índice `ix_document_owner_id`;
- foreign key nomeada `fk_document_owner_id_users`.

Foram adicionados testes para:

- persistência de usuário;
- unicidade de email;
- relacionamento entre usuário e documento;
- navegação por `document.owner`;
- navegação por `user.documents`;
- rejeição de `owner_id` inexistente pelo PostgreSQL.

Após a mudança, a suíte completa apresentou:

`58 passed`

O comando:

`alembic check`

retornou:

`No new upgrade operations detected.`

Isso confirma que os models, a migration e o schema atual do PostgreSQL estavam sincronizados ao final desta etapa.

## Próximas etapas

- implementar password hashing;
- criar contrato de cadastro;
- implementar login;
- gerar e validar JWT;
- resolver `current_user`;
- atribuir ownership na criação de documentos;
- filtrar documentos e chunks pelo usuário autenticado;
- isolar busca textual, semântica e híbrida;
- tornar `document.owner_id` obrigatório;
- adicionar testes com dois usuários para impedir vazamento entre contas.
