from aws_cdk import RemovalPolicy
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_s3 as s3
from constructs import Construct


class DrinkStorageConstruct(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id)

        # Criar bucket S3 para armazenar receitas e imagens
        self.recipes_bucket = s3.Bucket(
            self,
            "DrinkRecipesBucket",
            removal_policy=RemovalPolicy.RETAIN,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,
        )

        # Criar tabela DynamoDB para armazenar as receitas
        self.recipes_table = dynamodb.Table(
            self,
            "DrinkRecipesTable",
            partition_key=dynamodb.Attribute(name="recipe_id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
        )
