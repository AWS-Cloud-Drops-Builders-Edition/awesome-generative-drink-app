from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_lambda as _lambda
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from constructs import Construct
from infrastructure.drink.constructs.api import DrinkApiConstruct
from infrastructure.drink.constructs.secrets import DrinkSecretsConstruct
from infrastructure.drink.constructs.storage import DrinkStorageConstruct
from infrastructure.drink.constructs.workflow import DrinkWorkflowConstruct


class AwesomeGenerativeDrinkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Criar Lambda Layer comum para todas as funções
        lambda_layer = PythonLayerVersion(
            self,
            "CommonDrinkAppLayer",
            entry=".build/layer",
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            description="Common layer for Lambda functions",
        )

        # Criar constructs
        storage = DrinkStorageConstruct(self, "DrinkStorage")
        secrets = DrinkSecretsConstruct(self, "DrinkSecrets")

        workflow = DrinkWorkflowConstruct(
            self,
            "DrinkWorkflow",
            lambda_layer=lambda_layer,
            recipes_table=storage.recipes_table,
            recipes_bucket=storage.recipes_bucket,
            sendgrid_secret=secrets.sendgrid_secret,
        )

        DrinkApiConstruct(
            self,
            "DrinkApi",
            lambda_layer=lambda_layer,
            state_machine=workflow.state_machine,
        )

        # Exportar recursos para testes de integração
        CfnOutput(self, "DrinkRecipesTableName", value=storage.recipes_table.table_name, export_name="recipes-table-name")

        CfnOutput(self, "DrinkRecipesBucketName", value=storage.recipes_bucket.bucket_name, export_name="recipes-bucket-name")
