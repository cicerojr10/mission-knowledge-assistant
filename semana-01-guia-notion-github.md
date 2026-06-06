# Semana 1 - Fundamentos de API profissional para Aplicacoes de IA/LLM

**Projeto-base:** Mission Knowledge Assistant  
**Trilha:** Engenheiro de Aplicacoes de IA (LLM)  
**Foco da semana:** criar a base profissional do projeto: API, organizacao, GitHub, documentacao, testes e Docker inicial.

## Por que esta semana existe

Antes de estudar RAG, embeddings, guardrails e evals, voce precisa ter uma base de engenharia: uma API organizada, versionada no GitHub, com rotas claras, logs, validacao, testes e documentacao.

No trabalho real, um sistema de IA aplicada nao e apenas um prompt. Ele e uma aplicacao. Essa aplicacao precisa receber requisicoes, validar dados, chamar servicos, registrar logs, responder erros corretamente, ter testes e ser compreensivel para outras pessoas do time.

## Resultado esperado ao final da semana

Ao final da Semana 1, voce deve ter um repositorio GitHub com:

- [ ] API FastAPI rodando localmente.
- [ ] Endpoint `GET /health` funcionando.
- [ ] Endpoint `POST /documents` com armazenamento em memoria.
- [ ] Estrutura de pastas organizada.
- [ ] README inicial explicando o projeto.
- [ ] Diario tecnico diario em Markdown.
- [ ] Pelo menos 7 commits pequenos.
- [ ] Issues ou checklist de tarefas.
- [ ] Testes basicos com pytest.
- [ ] Dockerfile inicial.
- [ ] ADR-001 explicando uma decisao tecnica.

## Como estudar todos os dias

Use este formato fixo:

1. **Conceito:** entenda a ideia do dia.
2. **Papel no trabalho real:** entenda onde isso aparece numa empresa.
3. **Implementacao pequena:** escreva pouco codigo, mas funcionando.
4. **Teste:** rode, quebre, corrija.
5. **Registro tecnico:** anote o que aprendeu.
6. **Commit:** salve no GitHub com mensagem clara.

## Check-in diario

Copie este bloco no seu diario tecnico todos os dias:

```md
## Check-in do dia

Data:
Tempo disponivel hoje:
Energia de 1 a 5:
Objetivo principal do dia:

### Antes de codar
- [ ] Li o objetivo do dia.
- [ ] Entendi por que isso existe no trabalho real.
- [ ] Sei qual arquivo vou alterar.

### Durante o estudo
- [ ] Executei os comandos.
- [ ] Testei a API ou o codigo.
- [ ] Anotei erros e solucoes.

### Final do dia
- [ ] Fiz commit no Git.
- [ ] Atualizei o diario tecnico.
- [ ] Atualizei o README se necessario.
- [ ] Sei qual e o proximo passo.

Resumo do que aprendi:
Erro principal que apareceu:
Como resolvi:
Duvida que ficou:
Proximo passo:
```

---

# Dia 1 - Criar a API minima e entender o endpoint /health

## Objetivo

Criar a primeira versao da API com FastAPI e entender o papel de um endpoint de saude em producao.

## Conceito do dia

Uma API e um contrato entre sistemas. Quando voce cria um endpoint, voce esta definindo uma forma padronizada para outro sistema conversar com sua aplicacao.

O endpoint `GET /health` e usado para verificar se a aplicacao esta viva. Em empresas, esse tipo de endpoint pode ser usado por load balancers, sistemas de monitoramento, Kubernetes, ECS, scripts de deploy e ferramentas de observabilidade.

## O que aprender hoje

- O que e uma API.
- O que e FastAPI.
- O que e uma rota HTTP.
- O que significa `GET`.
- O que e JSON.
- Como rodar um servidor local.
- Como testar uma API no navegador ou terminal.

## Tarefas

- [ ] Criar pasta do projeto.
- [ ] Criar ambiente virtual Python.
- [ ] Instalar FastAPI e Uvicorn.
- [ ] Criar `app/main.py`.
- [ ] Implementar `GET /health`.
- [ ] Rodar a API localmente.
- [ ] Abrir `/docs` no navegador.
- [ ] Testar `/health`.
- [ ] Fazer primeiro commit.
- [ ] Escrever diario tecnico.

## Comandos

### Criar ambiente virtual no Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install fastapi uvicorn
pip freeze > requirements.txt
```

### Rodar a API

```powershell
uvicorn app.main:app --reload
```

### Testar no navegador

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## Codigo base

```python
from fastapi import FastAPI

app = FastAPI(title="Mission Knowledge Assistant")

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

## Explicacao linha por linha

`from fastapi import FastAPI` importa a classe principal usada para criar a API.

`app = FastAPI(...)` cria a instancia da aplicacao. E como dizer: "este e o servidor da minha API".

`@app.get("/health")` registra uma rota HTTP do tipo GET no caminho `/health`.

`def health_check()` e a funcao executada quando alguem chama esse endpoint.

`return {"status": "ok"}` devolve um JSON simples informando que a aplicacao esta viva.

## Commit sugerido

```bash
git add .
git commit -m "create initial FastAPI health endpoint"
```

## Entrega do dia

- [ ] API responde `{"status":"ok"}` em `/health`.
- [ ] Documentacao automatica abre em `/docs`.
- [ ] Primeiro commit feito.

---

# Dia 2 - Estrutura profissional de projeto

## Objetivo

Organizar a API em pastas e arquivos parecidos com um projeto real.

## Conceito do dia

No comeco, colocar tudo em `main.py` funciona. Mas em projeto real isso vira bagunca. Times separam responsabilidades em arquivos: rotas, schemas, configuracao, servicos e testes.

## O que aprender hoje

- Por que separar arquivos.
- O que e router.
- O que e schema.
- O que e configuracao.
- Como manter `main.py` limpo.

## Estrutura esperada

```text
mission-knowledge-assistant/
  app/
    main.py
    config.py
    schemas.py
    routes/
      health.py
      documents.py
  tests/
  docs/
  requirements.txt
  README.md
```

## Papel no trabalho real

Quando outro desenvolvedor entra no time, ele precisa entender rapidamente onde cada coisa fica. Estrutura boa reduz retrabalho e facilita manutencao.

## Tarefas

- [ ] Criar pasta `app/routes`.
- [ ] Mover rota `/health` para `routes/health.py`.
- [ ] Criar `config.py`.
- [ ] Criar `schemas.py`.
- [ ] Importar router no `main.py`.
- [ ] Rodar API e confirmar que nada quebrou.
- [ ] Atualizar README com estrutura do projeto.
- [ ] Fazer commit.

## Codigo esperado em `app/routes/health.py`

```python
from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
def health_check():
    return {"status": "ok"}
```

## Codigo esperado em `app/main.py`

```python
from fastapi import FastAPI
from app.routes.health import router as health_router

app = FastAPI(title="Mission Knowledge Assistant")
app.include_router(health_router)
```

## Commit sugerido

```bash
git add .
git commit -m "organize FastAPI project structure"
```

## Entrega do dia

- [ ] Estrutura de pastas criada.
- [ ] `/health` continua funcionando.
- [ ] README atualizado.

---

# Dia 3 - GitHub como diario de engenharia

## Objetivo

Usar GitHub nao so para salvar codigo, mas para registrar aprendizado, tarefas e decisoes.

## Conceito do dia

No trabalho, GitHub/GitLab/Bitbucket sao usados para colaboracao. O historico de commits mostra como o projeto evoluiu. Issues mostram tarefas. Pull requests mostram revisao. README mostra como usar o projeto.

## O que aprender hoje

- Repositorio.
- Commit pequeno.
- Branch.
- README.
- Issue.
- Diario tecnico.
- Pull request simulado.

## Tarefas

- [ ] Criar repositorio no GitHub.
- [ ] Subir o projeto.
- [ ] Criar `docs/diario-tecnico.md`.
- [ ] Criar `docs/checkins/semana-01-checkin.md`.
- [ ] Criar uma issue para cada dia da semana.
- [ ] Criar branch `feature/github-docs`.
- [ ] Atualizar README.
- [ ] Fazer commit e push.

## Comandos

```bash
git init
git add .
git commit -m "initial project setup"
git branch -M main
git remote add origin <URL_DO_SEU_REPOSITORIO>
git push -u origin main
```

## Padrao de commits

Use mensagens claras:

```text
create initial FastAPI app
add health route
organize project structure
add technical learning journal
add first document endpoint
```

## Papel no trabalho real

Um bom historico de Git mostra raciocinio. Em entrevista, seu repositorio precisa contar uma historia: problema, decisao, implementacao e aprendizado.

## Entrega do dia

- [ ] Repositorio no GitHub criado.
- [ ] README melhorado.
- [ ] Diario tecnico criado.
- [ ] Pelo menos 3 commits pequenos no historico.

---

# Dia 4 - HTTP, REST e endpoint de documentos em memoria

## Objetivo

Criar o primeiro endpoint de produto: cadastrar documentos em memoria.

## Conceito do dia

Antes de fazer RAG, voce precisa receber documentos. O endpoint `POST /documents` representa a entrada inicial da base de conhecimento.

Nesta semana ainda nao usaremos banco. Vamos salvar em memoria para entender a API primeiro. Na semana 2, isso vai para PostgreSQL.

## O que aprender hoje

- Metodo POST.
- Status code.
- Body JSON.
- Pydantic schema.
- UUID.
- Armazenamento em memoria.
- Contrato de API.

## Tarefas

- [ ] Criar schema `DocumentCreate`.
- [ ] Criar schema `DocumentResponse`.
- [ ] Criar rota `POST /documents`.
- [ ] Criar rota `GET /documents`.
- [ ] Testar no `/docs`.
- [ ] Testar com PowerShell.
- [ ] Atualizar README com endpoints.
- [ ] Fazer commit.

## Exemplo de request

```json
{
  "title": "Artemis Mission Overview",
  "content": "Artemis is a NASA program focused on returning humans to the Moon."
}
```

## Exemplo de response

```json
{
  "id": "uuid-gerado",
  "title": "Artemis Mission Overview",
  "content": "Artemis is a NASA program focused on returning humans to the Moon."
}
```

## Papel no trabalho real

Isso simula a criacao de um recurso via API. Em sistemas reais, quase tudo gira em torno de criar, consultar, atualizar e remover recursos.

## Entrega do dia

- [ ] `POST /documents` funcionando.
- [ ] `GET /documents` listando documentos cadastrados.
- [ ] README tem exemplos de request/response.

---

# Dia 5 - Configuracao, logs e tratamento de erros

## Objetivo

Comecar a tratar a API como aplicacao profissional: configuravel, observavel e previsivel em erros.

## Conceito do dia

Codigo profissional nao deve ter configuracoes espalhadas. URLs, chaves, ambiente e parametros devem ser configuraveis. Alem disso, erros precisam ser claros e logs ajudam a investigar problemas.

## O que aprender hoje

- Variaveis de ambiente.
- Arquivo `.env.example`.
- Logs.
- Erros HTTP.
- Validacao.
- Mensagens padronizadas.

## Tarefas

- [ ] Criar `.env.example`.
- [ ] Criar `config.py` com configuracoes basicas.
- [ ] Adicionar logging simples.
- [ ] Tratar documento vazio.
- [ ] Retornar erro 400 quando necessario.
- [ ] Atualizar README.
- [ ] Fazer commit.

## Exemplo de erro

Se o usuario tentar criar documento sem conteudo util, a API deve responder de forma clara.

```json
{
  "detail": "Document content cannot be empty."
}
```

## Papel no trabalho real

Quando uma API falha em producao, logs e erros claros aceleram investigacao. Sem isso, o time perde tempo tentando descobrir o que aconteceu.

## Entrega do dia

- [ ] `.env.example` criado.
- [ ] Erros basicos tratados.
- [ ] Logs aparecem no terminal.

---

# Dia 6 - Testes automatizados basicos

## Objetivo

Criar os primeiros testes automatizados da API.

## Conceito do dia

Teste automatizado e uma forma de garantir que uma funcionalidade continua funcionando apos mudancas. Em IA aplicada, alem de testes tradicionais, voce depois tera evals. Mas primeiro precisa entender testes normais.

## O que aprender hoje

- pytest.
- TestClient do FastAPI.
- Teste de endpoint.
- Assert.
- Regressao.
- Qualidade em CI.

## Tarefas

- [ ] Instalar pytest.
- [ ] Criar `tests/test_health.py`.
- [ ] Criar teste para `/health`.
- [ ] Criar teste para `POST /documents`.
- [ ] Rodar testes.
- [ ] Corrigir erros.
- [ ] Fazer commit.

## Comando

```bash
pip install pytest httpx
pip freeze > requirements.txt
pytest
```

## Papel no trabalho real

Antes de mandar codigo para producao, times maduros rodam testes automaticamente. Isso evita quebrar funcionalidades existentes.

## Entrega do dia

- [ ] `pytest` executa com sucesso.
- [ ] Pelo menos 2 testes criados.
- [ ] README explica como rodar testes.

---

# Dia 7 - Docker inicial, revisao e ADR

## Objetivo

Fechar a semana com um projeto mais profissional: Dockerfile, revisao do README, checklist final e primeira decisao arquitetural registrada.

## Conceito do dia

Docker empacota a aplicacao com suas dependencias. Isso ajuda a rodar o projeto de forma mais reproduzivel. ADR registra decisoes tecnicas e trade-offs.

## O que aprender hoje

- Dockerfile.
- Imagem.
- Container.
- Porta.
- Build.
- Run.
- ADR.
- Revisao tecnica semanal.

## Tarefas

- [ ] Criar `Dockerfile`.
- [ ] Criar `.dockerignore`.
- [ ] Rodar build da imagem.
- [ ] Rodar container local.
- [ ] Criar `docs/adr/ADR-001-fastapi.md`.
- [ ] Revisar README.
- [ ] Fazer checklist final da semana.
- [ ] Fazer commit final da semana.

## Dockerfile inicial

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Comandos

```bash
docker build -t mission-knowledge-assistant .
docker run -p 8000:8000 mission-knowledge-assistant
```

## ADR-001 sugerido

Tema: escolha do FastAPI para a API inicial.

Inclua:

- Contexto.
- Decisao.
- Motivos.
- Trade-offs.
- Consequencias.

## Entrega do dia

- [ ] Dockerfile criado.
- [ ] Projeto roda em container.
- [ ] ADR-001 criado.
- [ ] README revisado.
- [ ] Semana 1 finalizada.

---

# Checklist final da Semana 1

## Codigo

- [ ] API FastAPI criada.
- [ ] `/health` funcionando.
- [ ] `/documents` funcionando em memoria.
- [ ] Estrutura de pastas organizada.
- [ ] Configuracao basica criada.
- [ ] Tratamento de erro basico.
- [ ] Logs basicos.
- [ ] Testes automatizados.
- [ ] Dockerfile.

## GitHub

- [ ] Repositorio criado.
- [ ] README com explicacao do projeto.
- [ ] Commits pequenos.
- [ ] Diario tecnico.
- [ ] Check-ins diarios.
- [ ] ADR-001.
- [ ] Issues ou tarefas registradas.

## Aprendizado

- [ ] Sei explicar o que e uma API.
- [ ] Sei explicar o que e um endpoint.
- [ ] Sei explicar por que `/health` existe.
- [ ] Sei rodar FastAPI.
- [ ] Sei criar rota GET e POST.
- [ ] Sei usar Pydantic para validar entrada.
- [ ] Sei rodar testes basicos.
- [ ] Sei explicar o papel do Docker.
- [ ] Sei explicar o que e um ADR.

## Preparacao para a Semana 2

Na Semana 2, o foco sera persistencia real:

- PostgreSQL.
- Docker Compose.
- SQLAlchemy ou SQLModel.
- Tabelas de documentos.
- Migrations.
- Preparacao para chunks.

A Semana 1 cria a base. A Semana 2 começa a transformar a API em sistema com dados persistidos.