import json
import os

import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
tracer = Tracer()

# Configurações do Bedrock
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_TEXT_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
s3_client = boto3.client("s3")
bedrock_runtime = boto3.client("bedrock-runtime")

# Nome do bucket S3 (será definido via variável de ambiente)
RECIPES_BUCKET = os.environ.get("RECIPES_BUCKET")


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    Lambda function para gerar o texto da receita usando Amazon Bedrock.

    Args:
        event: Evento contendo os dados da receita
        context: Contexto da função Lambda

    Returns:
        dict: Evento original com informações adicionais sobre a receita gerada
    """
    try:
        logger.info("Generating drink recipe text with Bedrock")

        # Obter dados do evento
        recipe_id = event["recipe_id"]
        request_data = event["request"]

        # Construir prompt para o modelo
        prompt = create_recipe_prompt(request_data)

        # Chamar o Bedrock para gerar a receita
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": prompt}],
                }
            ),
        )

        # Processar resposta do Bedrock
        response_body = json.loads(response["body"].read().decode("utf-8"))
        recipe_text = response_body["content"][0]["text"]

        # Salvar receita no S3
        recipe_key = f"recipes/{recipe_id}/recipe.txt"
        s3_client.put_object(
            Bucket=RECIPES_BUCKET,
            Key=recipe_key,
            Body=recipe_text.encode("utf-8"),
            ContentType="text/plain",
        )

        logger.info(f"Recipe text generated and saved to S3: {recipe_key}")

        # Adicionar informações da receita ao evento para o próximo passo
        event["recipe"] = {"text": recipe_text, "s3_key": recipe_key}

        return event

    except Exception as error:
        logger.exception("Error generating drink recipe text")
        raise error


def create_recipe_prompt(request_data):
    """
    Cria o prompt para o modelo de linguagem gerar a receita.

    Args:
        request_data: Dados da solicitação da receita

    Returns:
        str: Prompt formatado
    """
    name = request_data.get("name", "")
    base_spirit = request_data.get("base_spirit", "")
    flavor_profile = request_data.get("flavor_profile", "")
    difficulty_level = request_data.get("difficulty_level", "")
    additional_notes = request_data.get("additional_notes", "")

    prompt = f"""Create a detailed cocktail recipe with the following specifications:

Name: {name}
Base Spirit: {base_spirit}
Flavor Profile: {flavor_profile}
Difficulty Level: {difficulty_level}
Additional Notes: {additional_notes}

Please include:
1. A brief introduction about the drink
2. List of ingredients with precise measurements
3. Step-by-step preparation instructions
4. Serving suggestions
5. Any interesting facts or history related to this type of cocktail

Format the recipe in a clear, professional style suitable for a cocktail recipe book.
"""

    return prompt
