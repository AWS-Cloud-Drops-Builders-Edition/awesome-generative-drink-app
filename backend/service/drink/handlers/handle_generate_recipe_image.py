import base64
import json
import os

import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
tracer = Tracer()

# Configurações do Bedrock
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_IMAGE_MODEL_ID", "stability.stable-diffusion-xl-v1")
s3_client = boto3.client("s3")
bedrock_runtime = boto3.client("bedrock-runtime")

# Nome do bucket S3 (será definido via variável de ambiente)
RECIPES_BUCKET = os.environ.get("RECIPES_BUCKET")


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    Lambda function para gerar a imagem da receita usando Amazon Bedrock.

    Args:
        event: Evento contendo os dados da receita
        context: Contexto da função Lambda

    Returns:
        dict: Evento original com informações adicionais sobre a imagem gerada
    """
    try:
        logger.info("Generating drink recipe image with Bedrock")

        # Obter dados do evento
        recipe_id = event["recipe_id"]
        request_data = event["request"]
        recipe_text = event["recipe"].get("text", "")

        # Construir prompt para o modelo de imagem
        prompt = create_image_prompt(request_data, recipe_text)

        # Chamar o Bedrock para gerar a imagem
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(
                {
                    "text_prompts": [{"text": prompt, "weight": 1.0}],
                    "cfg_scale": 7,
                    "steps": 50,
                    "seed": 0,
                    "width": 1024,
                    "height": 1024,
                }
            ),
        )

        # Processar resposta do Bedrock
        response_body = json.loads(response["body"].read().decode("utf-8"))
        image_base64 = response_body["artifacts"][0]["base64"]
        image_data = base64.b64decode(image_base64)

        # Salvar imagem no S3
        image_key = f"recipes/{recipe_id}/image.jpg"
        s3_client.put_object(
            Bucket=RECIPES_BUCKET,
            Key=image_key,
            Body=image_data,
            ContentType="image/jpeg",
        )

        logger.info(f"Recipe image generated and saved to S3: {image_key}")

        # Adicionar informações da imagem ao evento para o próximo passo
        event["recipe"]["image_s3_key"] = image_key

        return event

    except Exception as error:
        logger.exception("Error generating drink recipe image")
        raise error


def create_image_prompt(request_data, recipe_text):
    """
    Cria o prompt para o modelo de imagem gerar a visualização da receita.

    Args:
        request_data: Dados da solicitação da receita
        recipe_text: Texto da receita gerada

    Returns:
        str: Prompt formatado para geração de imagem
    """
    name = request_data.get("name", "")
    base_spirit = request_data.get("base_spirit", "")
    flavor_profile = request_data.get("flavor_profile", "")

    prompt = (
        f"A professional, high-quality photograph of a cocktail named '{name}' "
        f"made with {base_spirit} with a {flavor_profile} flavor profile. "
        f"The cocktail should be in an appropriate glass, garnished beautifully, "
        f"with perfect lighting and composition. The image should look like it belongs "
        f"in a high-end cocktail recipe book or luxury bar menu. "
        f"Studio lighting, high resolution, photorealistic."
    )

    return prompt
