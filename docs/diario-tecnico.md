# Dia 2 — Estrutura profissional de projeto

## O que fiz

Reorganizei a API FastAPI para separar responsabilidades em arquivos diferentes.

## O que aprendi

Aprendi que o `main.py` deve ser o ponto principal de montagem da aplicação, mas não precisa conter todas as rotas e regras.

Também aprendi que `APIRouter` permite separar endpoints por domínio, deixando o projeto mais organizado.

## Arquivos criados ou alterados

- `app/main.py`
- `app/config.py`
- `app/schemas.py`
- `app/routes/health.py`
- `app/__init__.py`
- `app/routes/__init__.py`
- `README.md`

## Relação com o trabalho real

Em empresas, projetos backend precisam ser organizados para facilitar manutenção, revisão de código, testes e colaboração. Separar rotas, configurações e schemas evita que o projeto vire um arquivo gigante difícil de entender.

## Erros ou cuidados

É importante rodar `uvicorn app.main:app --reload` a partir da raiz do projeto. Se eu rodar dentro da pasta `app`, o Python pode não encontrar o módulo corretamente.

## Próximo passo

Criar o primeiro endpoint de documentos e começar a entender contratos de entrada e saída com Pydantic.