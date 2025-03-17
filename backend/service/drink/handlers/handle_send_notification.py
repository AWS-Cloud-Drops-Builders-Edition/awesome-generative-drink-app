import base64
import json
import os

import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Attachment,
    Disposition,
    FileContent,
    FileName,
    FileType,
    Mail,
)

logger = Logger()
tracer = Tracer()

# Configurações do S3 e Secrets Manager
s3_client = boto3.client("s3")
secrets_client = boto3.client("secretsmanager")

# Nome do bucket S3 e secret (serão definidos via variáveis de ambiente)
RECIPES_BUCKET = os.environ.get("RECIPES_BUCKET")
SENDGRID_SECRET_NAME = os.environ.get("SENDGRID_SECRET_NAME")


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    Lambda function para enviar notificação por email usando SendGrid.

    Args:
        event: Evento contendo os dados da receita
        context: Contexto da função Lambda

    Returns:
        dict: Evento original com informações adicionais sobre a notificação
    """
    try:
        logger.info("Sending email notification with SendGrid")

        # Obter dados do evento
        request_data = event["request"]
        recipe_text = event["recipe"].get("text", "")
        recipe_image_key = event["recipe"].get("image_s3_key", "")
        recipient_email = request_data.get("email")
        drink_name = request_data.get("name", "Custom Drink")

        # Obter credenciais do SendGrid do Secrets Manager
        sendgrid_secret = get_sendgrid_secret()
        sendgrid_api_key = sendgrid_secret["api_key"]
        sender_email = sendgrid_secret["sender_email"]

        # Baixar a imagem do S3
        image_object = s3_client.get_object(Bucket=RECIPES_BUCKET, Key=recipe_image_key)
        image_data = image_object["Body"].read()

        # Criar email
        message = Mail(
            from_email=sender_email,
            to_emails=recipient_email,
            subject=f"Your Custom Drink Recipe: {drink_name}",
            html_content=create_email_content(drink_name, recipe_text),
        )

        # Anexar a imagem
        encoded_image = base64.b64encode(image_data).decode()
        attachment = Attachment()
        attachment.file_content = FileContent(encoded_image)
        attachment.file_type = FileType("image/jpeg")
        attachment.file_name = FileName(f'{drink_name.replace(" ", "_")}.jpg')
        attachment.disposition = Disposition("attachment")
        message.attachment = attachment

        # Enviar email
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)

        logger.info(f"Email notification sent: {response.status_code}")

        # Adicionar informações da notificação ao evento
        event["notification"] = {
            "sent_to": recipient_email,
            "status": "SENT",
            "status_code": response.status_code,
        }

        return event

    except Exception as error:
        logger.exception("Error sending email notification")
        # Adicionar informações do erro ao evento, mas não falhar o fluxo
        event["notification"] = {"status": "FAILED", "error": str(error)}
        return event


def get_sendgrid_secret():
    """
    Obtém as credenciais do SendGrid do AWS Secrets Manager.

    Returns:
        dict: Credenciais do SendGrid (api_key e sender_email)
    """
    try:
        response = secrets_client.get_secret_value(SecretId=SENDGRID_SECRET_NAME)
        secret_string = response["SecretString"]
        return json.loads(secret_string)
    except Exception as error:
        logger.exception("Error retrieving SendGrid credentials")
        raise error


def create_email_content(drink_name, recipe_text):
    """
    Cria o conteúdo HTML do email.

    Args:
        drink_name: Nome da bebida
        recipe_text: Texto da receita

    Returns:
        str: Conteúdo HTML formatado
    """
    # Formatar o texto da receita para HTML (substituir quebras de linha por <br>)
    formatted_recipe = recipe_text.replace("\n", "<br>")

    html_content = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #8B4513; }}
                .recipe {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Your Custom Drink Recipe: {drink_name}</h1>
                <p>Thank you for using our Awesome Generative Drink App! Here's your custom recipe:</p>
                <div class="recipe">
                    {formatted_recipe}
                </div>
                <p>We've attached an image of what your drink might look like. Enjoy!</p>
                <div class="footer">
                    <p>This recipe was generated by AI and may need adjustments to suit your taste.</p>
                    <p>© Awesome Generative Drink App</p>
                </div>
            </div>
        </body>
    </html>
    """

    return html_content
