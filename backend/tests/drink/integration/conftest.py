import os
import uuid

import boto3
import pytest
from infrastructure.drink.stack_utils import generate_stack_name


@pytest.fixture(scope="session")
def aws_resources():
    """Fixture que retorna os recursos da AWS necessários para os testes."""
    cfn = boto3.client("cloudformation")
    stack_name = generate_stack_name()

    # Obter outputs da stack
    response = cfn.describe_stacks(StackName=stack_name)
    outputs = {output["OutputKey"]: output["OutputValue"] for output in response["Stacks"][0]["Outputs"]}

    return {"table_name": outputs["DrinkRecipesTableName"], "bucket_name": outputs["DrinkRecipesBucketName"]}


@pytest.fixture(scope="session", autouse=True)
def setup_lambda_environment(aws_resources):
    """Configura as variáveis de ambiente necessárias para todas as funções Lambda."""
    # Guardar as variáveis originais (se existirem)
    original_env = {
        "DRINK_RECIPES_TABLE": os.environ.get("DRINK_RECIPES_TABLE"),
    }

    # Configurar as variáveis para os testes
    os.environ["DRINK_RECIPES_TABLE"] = aws_resources["table_name"]

    yield

    # Restaurar as variáveis originais
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


class MockContext:
    """Mock do contexto Lambda para testes."""

    def __init__(self):
        self.function_name = "test-function"
        self.memory_limit_in_mb = 128
        self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
        self.aws_request_id = str(uuid.uuid4())


@pytest.fixture
def lambda_context():
    """Fixture que retorna um contexto Lambda mockado."""
    return MockContext()
