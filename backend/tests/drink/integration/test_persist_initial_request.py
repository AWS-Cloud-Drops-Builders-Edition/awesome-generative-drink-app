import uuid
from datetime import UTC, datetime

import boto3
import pytest


# Importação tardia para garantir que as variáveis de ambiente já estejam configuradas
@pytest.fixture
def lambda_handler():
    from service.drink.handlers.handle_persist_initial_request import lambda_handler

    return lambda_handler


from service.drink.models.drink_request import DrinkRequest


@pytest.mark.integration
def test_persist_initial_request(aws_resources, lambda_context, lambda_handler):
    """Testa a persistência da requisição inicial no DynamoDB."""
    # Preparar
    recipe_id = str(uuid.uuid4())
    timestamp = datetime.now(UTC).isoformat()

    request = DrinkRequest(customer_name="Test Customer", mood="happy", flavor="fruity", fruit=["apple"], liquids=["water"])

    event = {"recipe_id": recipe_id, "timestamp": timestamp, "request": request.model_dump()}

    # Executar
    result = lambda_handler(event, lambda_context)

    # Verificar
    assert result == event  # A função deve retornar o evento original

    # Verificar se os dados foram persistidos no DynamoDB
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(aws_resources["table_name"])
    item = table.get_item(Key={"recipe_id": recipe_id})["Item"]

    assert item["recipe_id"] == recipe_id
    assert item["timestamp"] == timestamp
    assert item["request"] == request.model_dump()
    assert item["status"] == "PROCESSING"
