import os

import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
tracer = Tracer()
dynamodb = boto3.resource("dynamodb")

# Nome da tabela do DynamoDB (será definido via variável de ambiente)
DRINK_RECIPES_TABLE = os.environ.get("DRINK_RECIPES_TABLE")


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    Lambda function para persistir a solicitação inicial no DynamoDB.

    Args:
        event: Evento contendo os dados da receita
        context: Contexto da função Lambda

    Returns:
        dict: Evento original com informações adicionais
    """
    try:
        logger.info("Persisting initial drink recipe request")

        # Obter dados do evento
        recipe_id = event["recipe_id"]
        timestamp = event["timestamp"]
        request_data = event["request"]

        # Referência para a tabela do DynamoDB
        table = dynamodb.Table(DRINK_RECIPES_TABLE)

        # Inserir item na tabela
        table.put_item(
            Item={
                "recipe_id": recipe_id,
                "timestamp": timestamp,
                "request": request_data,
                "status": "PROCESSING",
            }
        )

        logger.info(f"Request persisted successfully with ID: {recipe_id}")

        # Retornar o evento original para continuar o fluxo do Step Function
        return event

    except Exception as error:
        logger.exception("Error persisting drink recipe request")
        raise error
