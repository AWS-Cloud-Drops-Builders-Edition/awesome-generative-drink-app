# Backend

Este é o backend da aplicação, construído com AWS CDK, Lambda e API Gateway.

## Estrutura do Projeto

- `app.py`: O arquivo principal do CDK que define a stack.
- `backend/backend_stack.py`: Define os recursos AWS para o backend.
- `lambda/handler.py`: Contém o manipulador da função Lambda e a lógica da API.
- `pyproject.toml`: Arquivo de configuração do Poetry com as dependências do projeto.

## Gerenciamento de Dependências

Este projeto utiliza Poetry para gerenciamento de dependências. O arquivo `pyproject.toml` contém todas as dependências necessárias para o projeto.

## Configuração e Implantação

1. Certifique-se de ter o AWS CDK e Poetry instalados e configurados.
2. Navegue até o diretório `backend`.
3. Execute `poetry install` para instalar as dependências do projeto.
4. Execute `poetry run cdk deploy` para implantar a stack em sua conta AWS.

## Endpoints da API

- GET /: Retorna uma mensagem de saudação. Aceita um parâmetro de consulta opcional `name`.

## Função Lambda

A função Lambda usa AWS Lambda Powertools para registro, rastreamento e tratamento de API.

Para mais detalhes, consulte os comentários e docstrings nos respectivos arquivos.