# Diário Técnico — Mission Knowledge Assistant

Este diário registra minha evolução prática na construção do projeto **Mission Knowledge Assistant**, uma aplicação de IA aplicada com foco em APIs, LLMs, RAG, embeddings, guardrails, evals, segurança, observabilidade e fundamentos de produção.

O objetivo deste arquivo não é apenas guardar anotações, mas documentar raciocínio técnico, decisões, erros, correções e a relação entre cada etapa do projeto e o dia a dia real de trabalho.

---

# Semana 1 — Base profissional de API

## Dia 1 — API mínima com FastAPI

Data:
Tempo estudado:
Energia de 1 a 5:

### Conceito estudado

Estudei o conceito de API e criei a primeira versão da aplicação usando FastAPI.

O foco foi implementar um endpoint simples:

```text
GET /health
```

Esse endpoint serve para verificar se a aplicação está viva.

### Onde isso aparece no trabalho real

Em empresas, endpoints de saúde são usados por ferramentas de monitoramento, infraestrutura, deploy, load balancers e orquestradores para verificar se um serviço está funcionando.

Mesmo sendo simples, `/health` representa uma prática comum em aplicações reais.

### O que implementei

Criei a estrutura inicial do projeto e o arquivo:

```text
app/main.py
```

Implementei uma API FastAPI com resposta básica para `/health`.

Também criei arquivos iniciais como:

```text
README.md
requirements.txt
.gitignore
```

### Comandos usados

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install fastapi uvicorn
pip freeze > requirements.txt
uvicorn app.main:app --reload
```

### Erros encontrados

Tentei acessar a API e recebi erro de conexão recusada no navegador.

Depois percebi que o servidor não tinha subido corretamente porque eu rodei o comando a partir da pasta errada.

### Como resolvi

Entendi que o comando:

```powershell
uvicorn app.main:app --reload
```

precisa ser executado a partir da raiz do projeto.

O caminho `app.main:app` significa:

```text
app = pasta
main = arquivo main.py
app = variável FastAPI dentro do arquivo
```

### O que ainda não entendi

Preciso praticar melhor como o Python resolve caminhos de importação e como isso muda dependendo da pasta onde o comando é executado.

### Commit do dia

```text
create initial FastAPI health endpoint
```

### Próximo passo

Organizar melhor a estrutura do projeto, separando rotas, configurações e schemas.

---

## Dia 2 — Estrutura profissional do projeto

Data:
Tempo estudado:
Energia de 1 a 5:

### Conceito estudado

Estudei organização de projeto em FastAPI.

O objetivo foi deixar de concentrar tudo em `main.py` e começar a separar responsabilidades em arquivos e pastas.

### Onde isso aparece no trabalho real

Em projetos profissionais, um único arquivo com todas as rotas, configurações e regras rapidamente vira difícil de manter.

Separar responsabilidades facilita manutenção, revisão de código, testes e colaboração entre desenvolvedores.

### O que implementei

Organizei a estrutura do projeto com arquivos como:

```text
app/main.py
app/config.py
app/schemas.py
app/routes/health.py
app/__init__.py
app/routes/__init__.py
```

O `main.py` passou a funcionar como ponto principal de montagem da aplicação.

A rota `/health` foi movida para um router separado.

### Comandos usados

```powershell
mkdir app\routes -Force
New-Item app\__init__.py -ItemType File -Force
New-Item app\routes\__init__.py -ItemType File -Force
New-Item app\config.py -ItemType File -Force
New-Item app\schemas.py -ItemType File -Force
New-Item app\routes\health.py -ItemType File -Force
uvicorn app.main:app --reload
```

### Erros encontrados

O principal cuidado foi garantir que o comando do Uvicorn continuasse sendo executado na raiz do projeto.

Também precisei entender que criar um arquivo de rota não basta: é necessário conectar o router no `main.py`.

### Como resolvi

No `main.py`, importei o router de health e usei:

```python
app.include_router(health_router)
```

Assim a rota definida em `app/routes/health.py` passou a fazer parte da aplicação principal.

### O que ainda não entendi

Preciso praticar mais a diferença entre módulo, pacote, arquivo e import em Python.

### Commit do dia

```text
organize FastAPI project structure
```

### Próximo passo

Usar o GitHub como diário de engenharia, registrando aprendizado, decisões e check-ins.

---

## Dia 3 — GitHub como diário de engenharia

Data:
Tempo estudado:
Energia de 1 a 5:

### Conceito estudado

Estudei como usar o GitHub não apenas para guardar código, mas também como evidência de aprendizado técnico.

O foco foi criar documentação do projeto, check-ins e ADRs.

ADR significa **Architecture Decision Record**, ou registro de decisão arquitetural.

### Onde isso aparece no trabalho real

Em equipes profissionais, documentação ajuda outros desenvolvedores a entenderem o projeto, revisarem decisões e continuarem o trabalho sem depender apenas de explicações verbais.

Pull Requests, commits, README, check-ins e ADRs ajudam a contar a história técnica do projeto.

### O que implementei

Criei a estrutura de documentação:

```text
docs/
  adr/
    ADR-000-template.md
    ADR-001-fastapi.md
  checkins/
    semana-01-checkin.md
  semana-01-guia.md
```

Também atualizei o README para explicar a existência do diário de engenharia.

Criei a primeira ADR real:

```text
ADR-001 — Usar FastAPI como base da API
```

### Comandos usados

```powershell
mkdir docs -Force
mkdir docs\checkins -Force
mkdir docs\adr -Force
New-Item docs\checkins\semana-01-checkin.md -ItemType File -Force
New-Item docs\adr\ADR-000-template.md -ItemType File -Force
New-Item docs\adr\ADR-001-fastapi.md -ItemType File -Force
git checkout -b day-03-engineering-journal
git add .
git commit -m "add engineering journal and architecture decision records"
git push -u origin day-03-engineering-journal
```

### Erros encontrados

Criei um arquivo com nome errado:

```text
ADR-000-templade.md
```

O correto era:

```text
ADR-000-template.md
```

Também tive conflito ao tentar trocar de branch com alterações locais não salvas.

### Como resolvi

Usei o Git para proteger as alterações e corrigi a estrutura.

Removi o arquivo com nome errado e mantive apenas o arquivo correto.

Também entendi que antes de trocar de branch é necessário deixar o estado limpo, fazendo commit, stash ou descartando alterações.

### O que ainda não entendi

Preciso praticar melhor o fluxo completo:

```text
branch
commit
push
pull request
merge
git pull local
```

### Commit do dia

```text
add engineering journal and architecture decision records
complete day 3 check-in and remove typo ADR file
```

### Próximo passo

Criar o primeiro recurso real da API: endpoints de documentos.

---

## Dia 4 — Endpoint de documentos com Pydantic

Data:
Tempo estudado:
Energia de 1 a 5:

### Conceito estudado

Estudei criação de endpoints com entrada e saída estruturadas usando Pydantic.

O objetivo foi criar os primeiros endpoints ligados ao futuro fluxo de RAG:

```text
POST /documents
GET /documents
```

### Onde isso aparece no trabalho real

Em uma aplicação real, antes de gerar embeddings, fazer busca vetorial ou chamar um LLM, o sistema precisa receber, validar e organizar documentos.

Esse é o primeiro passo do fluxo:

```text
documento
→ texto
→ chunks
→ embeddings
→ banco vetorial
→ busca semântica
→ resposta com LLM
```

### O que implementei

Criei schemas em `app/schemas.py`:

```text
DocumentCreate
DocumentResponse
```

Criei o arquivo:

```text
app/routes/documents.py
```

Implementei:

```text
POST /documents
GET /documents
```

Usei armazenamento temporário em memória com uma lista chamada `_DOCUMENTS`.

### Comandos usados

```powershell
git checkout main
git pull origin main
git checkout -b day-04-documents-endpoint
uvicorn app.main:app --reload
```

Também testei no navegador:

```text
http://127.0.0.1:8000/docs
```

### Erros encontrados

Precisei entender que criar `documents.py` não torna a rota ativa automaticamente.

Também precisei entender que armazenamento em memória desaparece quando a aplicação reinicia.

### Como resolvi

Conectei o router de documentos no `main.py`:

```python
app.include_router(documents_router)
```

Assim os endpoints apareceram no `/docs`.

### O que ainda não entendi

Preciso entender melhor como esse armazenamento em memória será substituído por PostgreSQL na próxima fase.

### Commit do dia

```text
add in-memory document endpoints
```

### Próximo passo

Melhorar configuração, logs e tratamento de erros para aproximar a API de uma aplicação profissional.

---

## Dia 5 — Configuração, logs e tratamento de erros

Data:
Tempo estudado:
Energia de 1 a 5:

### Conceito estudado

Estudei configuração por ambiente, variáveis de ambiente, logs e tratamento de erros.

O objetivo foi preparar a API para se comportar melhor em diferentes ambientes e facilitar investigação quando algo acontecer.

### Onde isso aparece no trabalho real

Aplicações reais geralmente rodam em ambientes diferentes:

```text
local
development
staging
production
```

Cada ambiente pode ter configurações próprias, como nível de log, nome da aplicação, URL de banco e chaves de API.

Logs ajudam times de desenvolvimento, DevOps, SRE e suporte a investigar o comportamento da aplicação.

### O que implementei

Criei:

```text
.env.example
app/logging_config.py
```

Melhorei:

```text
app/config.py
app/main.py
app/routes/documents.py
```

Adicionei configurações como:

```text
APP_NAME
APP_VERSION
APP_ENV
LOG_LEVEL
MAX_DOCUMENT_CONTENT_LENGTH
```

Também adicionei logs e tratamento para entradas inválidas em documentos.

### Comandos usados

```powershell
git checkout main
git pull origin main
git checkout -b day-05-config-logging-errors
uvicorn app.main:app --reload
```

Também testei variáveis de ambiente no PowerShell:

```powershell
$env:LOG_LEVEL="DEBUG"
$env:APP_ENV="development"
uvicorn app.main:app --reload
```

### Erros encontrados

Ao chegar no Dia 6, percebi que parte das validações esperadas pelos testes não tinha ficado realmente implementada ou não estava completa.

Os testes mostraram que a API ainda aceitava título vazio com espaços e conteúdo acima do limite permitido.

### Como resolvi

Essa correção ficou para ser feita no Dia 6, guiada pelos testes automatizados.

Isso mostrou que testes servem para revelar regras de negócio incompletas.

### O que ainda não entendi

Preciso entender melhor a diferença entre:

```text
configuração hardcoded
variável de ambiente
arquivo .env
.env.example
secrets de produção
```

### Commit do dia

```text
add configuration logging and document error handling
```

### Próximo passo

Criar testes automatizados para garantir que os endpoints principais continuem funcionando conforme o projeto evolui.

---

## Dia 6 — Testes automatizados com pytest

Data:
Tempo estudado:
Energia de 1 a 5:

### Conceito estudado

Estudei testes automatizados com `pytest` e `TestClient` do FastAPI.

O objetivo foi validar automaticamente os endpoints principais da API, sem depender apenas de testes manuais pelo navegador ou pelo `/docs`.

### Onde isso aparece no trabalho real

Em projetos profissionais, testes automatizados ajudam a garantir que a aplicação continue funcionando depois de mudanças no código.

Eles podem rodar localmente, em Pull Requests e em pipelines de CI/CD.

Isso reduz o risco de quebrar funcionalidades existentes conforme o sistema evolui.

### O que implementei

Criei a pasta:

```text
tests/
```

Criei testes para:

```text
GET /health
POST /documents
GET /documents
rejeição de título vazio
rejeição de conteúdo vazio
rejeição de conteúdo grande demais
```

Também criei o arquivo:

```text
pytest.ini
```

para configurar o caminho de importação do projeto.

### Comandos usados

```powershell
pip install pytest httpx
pip freeze > requirements.txt
pytest
```

### Erros encontrados

Primeiro apareceu o erro:

```text
ModuleNotFoundError: No module named 'app'
```

Depois de corrigir o caminho de importação, os testes rodaram, mas dois falharam:

```text
esperava 400, mas recebeu 201
esperava 413, mas recebeu 201
```

Isso mostrou que a API ainda aceitava título vazio com espaços e conteúdo acima do limite permitido.

### Como resolvi

Criei ou confirmei os arquivos:

```text
app/__init__.py
app/routes/__init__.py
pytest.ini
```

No `pytest.ini`, adicionei:

```ini
[pytest]
pythonpath = .
testpaths = tests
```

Depois corrigi a implementação em `app/routes/documents.py`, adicionando validações para:

```text
título vazio após strip()
conteúdo vazio após strip()
conteúdo acima de settings.max_document_content_length
```

Também confirmei que `app/config.py` possui:

```python
max_document_content_length: int = int(
    os.getenv("MAX_DOCUMENT_CONTENT_LENGTH", "5000")
)
```

### O que ainda não entendi

Ainda preciso praticar melhor:

```text
como o pytest encontra os módulos do projeto
por que fixtures limpam estado entre testes
como testes mudam quando o armazenamento deixar de ser em memória e passar para PostgreSQL
```

### Commit do dia

```text
add automated tests and fix document validation
```

### Próximo passo

Preparar o projeto para Docker no Dia 7, fechando a base da Semana 1.

Também encontrei um erro ao tentar rodar o container:

```text
exec: "uvicorn": executable file not found in $PATH

Isso aconteceu porque o container não usa a .venv local. Ele instala apenas o que está declarado no requirements.txt.

Corrigi instalando uvicorn[standard], atualizando o requirements.txt e alterando o CMD do Dockerfile para usar:

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

Esse registro é bom porque mostra aprendizado real.

## 6. Commit do Dia 7

Depois de revisar, rode:

```powershell
git add .
git commit -m "add Docker support and complete week 1 review"


# Retrospectiva consolidada — Semanas 2 a 4

## Nota de continuidade

O diário técnico não foi atualizado diariamente durante as Semanas 2, 3 e 4.

O desenvolvimento continuou sendo registrado por código, commits, Pull Requests, ADRs, check-ins, testes e documentos de experimentos.

Em vez de reconstruir artificialmente entradas diárias, esta retrospectiva registra os principais aprendizados do período com base no trabalho realmente realizado.

## Semana 2 — Persistência

A principal evolução foi substituir armazenamento temporário em memória por persistência real com PostgreSQL.

O projeto passou a utilizar SQLModel, Alembic e Docker Compose.

Comecei a compreender melhor que modelo da aplicação, schema da API, schema do banco e migration representam responsabilidades diferentes.

Um aprendizado importante foi perceber que alterar uma classe Python não altera automaticamente um banco já existente.

## Semana 3 — Chunking e busca textual

O projeto evoluiu para a estrutura:

Document → Chunk → persistência → retrieval

Foi criada uma estratégia inicial de chunking com `chunk_size = 500` e `overlap = 50`.

Também foi implementada busca textual simples com `ILIKE`.

Essa escolha foi intencionalmente básica.

O objetivo era primeiro possuir uma baseline compreensível e testável para posteriormente comparar com recuperação semântica.

## Semana 4 — Embeddings e pgvector

A maior evolução arquitetural até este ponto aconteceu na Semana 4.

O projeto passou a gerar embeddings com `sentence-transformers/all-MiniLM-L6-v2`, utilizando vetores de 384 dimensões.

Os embeddings foram associados aos chunks e persistidos no PostgreSQL com pgvector.

A busca passou a incluir recuperação semântica por distância de cosseno.

## Ranking não é relevância

Um dos aprendizados mais importantes foi perceber que um mecanismo de ranking sempre consegue ordenar candidatos disponíveis.

O primeiro colocado não é automaticamente relevante.

Isso levou à separação entre:

`top_k` → quantidade

`max_distance` → aceitação

Depois disso, foi criado um experimento controlado para observar o comportamento dessas decisões.

O valor `0.60` apresentou o melhor equilíbrio no pequeno corpus utilizado, mas não deve ser tratado como threshold universal.

## Busca híbrida

Textual e semântico mostraram características complementares.

Como extensão do plano original, foi implementada busca híbrida com Reciprocal Rank Fusion.

O RRF permitiu combinar rankings sem somar diretamente sinais com escalas diferentes.

O projeto passou a possuir três estratégias independentes:

- textual;
- semântica;
- híbrida.

## Testes e evidência

Ao final da Semana 4, a suíte completa chegou a:

`54 passed`

Mais importante que o número foi a mudança na forma de raciocinar.

Passei a perguntar não apenas se o código funciona, mas também:

- qual comportamento quero garantir?
- como posso provar isso?
- quais casos enfraquecem minha hipótese?
- o que meu experimento realmente demonstra?
- o que ainda não posso afirmar?

## Evolução da metodologia de estudo

A Semana 4 também consolidou um processo de aprendizado mais completo:

estudar
→ implementar
→ testar
→ experimentar
→ documentar
→ revisar
→ explicar

Foram utilizados materiais técnicos e podcasts no NotebookLM.

Ao final do ciclo, gravei uma aula de aproximadamente 20 minutos explicando a evolução da arquitetura e as decisões tomadas.

A aula gravada passou a fazer parte da metodologia semanal porque implementar e explicar são competências diferentes.

## Mudança de mentalidade

No início do projeto, minha pergunta era frequentemente:

"Como implemento esta tecnologia?"

A pergunta está evoluindo para:

"Qual problema existe?"

"Qual é a solução mais simples que resolve esse problema?"

"Como valido a decisão?"

"Quais trade-offs estou aceitando?"

"Qual evidência eu realmente tenho?"

Essa mudança de raciocínio é uma das partes mais importantes do projeto para minha transição profissional.

## Estado ao final da Semana 4

O Mission Knowledge Assistant possui atualmente:

- FastAPI;
- PostgreSQL;
- SQLModel;
- Alembic;
- Docker;
- Pytest;
- Document → Chunk;
- busca textual;
- embeddings;
- pgvector;
- busca semântica;
- threshold de relevância;
- avaliação controlada;
- busca híbrida com RRF.

RAG ainda não foi implementado.

## Próximo passo

Antes da Semana 5, o próximo passo é comparar o projeto com vagas reais e identificar:

mercado
→ competências já demonstradas
→ gaps
→ prioridades

A próxima etapa técnica não deve existir apenas porque uma tecnologia é interessante.

Ela deve continuar ligada a um problema, a evidência e ao meu objetivo profissional.

## Security Slice ? progresso at? o Dia 4

Antes de iniciar RAG, o projeto passou a tratar autentica??o, autoriza??o e isolamento entre usu?rios como requisitos arquiteturais.

At? o Dia 4 foram implementados:

- modelo de usu?rios e relacionamento de propriedade com documentos;
- registro de usu?rios com senha armazenada por hash Argon2;
- autentica??o com JWT;
- endpoints de login e identifica??o do usu?rio autenticado;
- depend?ncia reutiliz?vel `get_current_user`;
- autentica??o obrigat?ria nas rotas de documentos;
- atribui??o de `Document.owner_id` pelo backend;
- listagem de documentos filtrada pelo usu?rio autenticado;
- prote??o da consulta de chunks por `document_id` e `owner_id`;
- resposta `404` para tentativa de acesso ao documento de outro usu?rio;
- constraint `NOT NULL` para `document.owner_id`.

O campo `owner_id` n?o faz parte de `DocumentCreate`.

Essa decis?o impede que o cliente escolha arbitrariamente o propriet?rio do documento.

A aplica??o identifica o usu?rio pelo token e utiliza seu ID ao persistir e consultar os dados.

Ao final do Dia 4, a su?te completa possui:

`98 passed`

A migration `1b2ec7d5f630` tornou obrigat?rio o propriet?rio de todo documento no PostgreSQL.

Os testes antigos que criavam documentos diretamente no banco tamb?m foram adaptados ao novo contrato de propriedade.

O Security Slice ainda n?o est? conclu?do.

As buscas textual, sem?ntica e h?brida ainda precisam receber o usu?rio autenticado e filtrar todos os resultados por ownership.

RAG continua adiado at? que esse isolamento seja garantido em todos os caminhos de retrieval.

Tamb?m permanecem registradas duas pend?ncias t?cnicas independentes:

- avisos de deprecia??o do Starlette/TestClient e do status HTTP 413;
- aviso de incompatibilidade da vers?o de collation do PostgreSQL usado no ambiente local.
