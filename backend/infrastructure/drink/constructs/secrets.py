from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct


class DrinkSecretsConstruct(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id)

        # Criar secret para armazenar as credenciais do SendGrid
        self.sendgrid_secret = secretsmanager.Secret(
            self,
            "SendGridSecret",
            description="SendGrid API key and sender email for notifications",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"sender_email":"noreply@example.com"}',
                generate_string_key="api_key",
            ),
        )
