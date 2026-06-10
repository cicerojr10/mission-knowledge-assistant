# Diario tecnico

Use este arquivo para registrar sua evolucao diaria.

## Dia X - Tema

Data:
Tempo estudado:
Energia de 1 a 5:

### Conceito estudado


### Onde isso aparece no trabalho real


### O que implementei


### Comandos usados

```bash

```

### Erros encontrados


### Como resolvi


### O que ainda nao entendi


### Commit do dia


### Proximo passo

---

## Dia 5 — Configuração, logs e tratamento de erros

### O que fiz

Melhorei a configuração da aplicação usando variáveis de ambiente e criei um arquivo `.env.example`.

Também adicionei uma configuração básica de logs em `app/logging_config.py` e inclui logs nos endpoints de documentos.

Além disso, melhorei o tratamento de erros para documentos com título vazio, conteúdo vazio e conteúdo acima do limite configurado.

### O que aprendi

Aprendi que configurações não devem ficar espalhadas pelo código. Usar variáveis de ambiente permite adaptar a aplicação para diferentes ambientes, como local, desenvolvimento, staging e produção.

Também aprendi que logs são fundamentais para investigar o comportamento da aplicação, mas é necessário cuidado para não registrar dados sensíveis.

### Relação com o trabalho real

Em empresas, logs ajudam times de desenvolvimento, SRE, DevOps e suporte a entender o que aconteceu em uma aplicação.

Também é comum que configurações importantes, como ambiente, nível de log, URL de banco e chaves de API, sejam controladas por variáveis de ambiente.

### Erros ou cuidados

Não devo enviar arquivos `.env` reais para o GitHub.

Também não devo registrar conteúdo sensível dos documentos nos logs.

### Próximo passo

Criar testes automatizados para garantir que os endpoints principais continuem funcionando conforme o projeto evolui.