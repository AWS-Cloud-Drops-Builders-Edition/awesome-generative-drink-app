import json
import os
import uuid
from datetime import datetime

import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.parser import parse
from aws_lambda_powertools.utilities.typing import LambdaContext
from service.drink.models.drink_request import DrinkRequest

logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver()
sfn_client = boto3.client("stepfunctions")

# Nome da máquina de estado do Step Functions (será definido via variável de ambiente)
STEP_FUNCTION_ARN = os.environ.get("DRINK_RECIPE_STEP_FUNCTION_ARN")


@app.post("/drink")
@tracer.capture_method
def handle_create_drink():
    try:
        # Parse do corpo da requisição
        drink_request = parse(event=app.current_event.body, model=DrinkRequest)

        # Gerar ID único para a receita
        recipe_id = str(uuid.uuid4())

        # Preparar input para o Step Function
        step_function_input = {
            "recipe_id": recipe_id,
            "timestamp": datetime.utcnow().isoformat(),
            "request": drink_request.model_dump(),
        }

        # Iniciar execução do Step Function
        response = sfn_client.start_execution(
            stateMachineArn=STEP_FUNCTION_ARN,
            name=f"DrinkRecipe-{recipe_id}",
            input=json.dumps(step_function_input),
        )

        logger.info(f"Step Function execution started: {response['executionArn']}")

        # Retornar resposta para o cliente
        return {
            "statusCode": 202,  # Accepted
            "body": {
                "message": "Drink recipe generation started",
                "recipe_id": recipe_id,
            },
        }
    except Exception:
        logger.exception("Error processing drink recipe request")
        return {"statusCode": 500, "body": {"message": "Error processing request"}}


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
