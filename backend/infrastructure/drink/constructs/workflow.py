from aws_cdk import Duration
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as tasks
from constructs import Construct


class DrinkWorkflowConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        lambda_layer: _lambda.LayerVersion,
        recipes_table: dynamodb.Table,
        recipes_bucket: s3.Bucket,
        sendgrid_secret: secretsmanager.Secret,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id)

        # Criar função Lambda para persistir a solicitação inicial
        self.persist_initial_lambda = _lambda.Function(
            self,
            "PersistInitialRequestFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset(".build/lambda"),
            handler="service.drink.handlers.handle_persist_initial_request.lambda_handler",
            layers=[lambda_layer],
            timeout=Duration.seconds(30),
            memory_size=128,
            environment={
                "DRINK_RECIPES_TABLE": recipes_table.table_name,
            },
        )

        # Conceder permissões para a função Lambda acessar a tabela DynamoDB
        recipes_table.grant_write_data(self.persist_initial_lambda)

        # Criar função Lambda para gerar o texto da receita
        self.generate_recipe_text_lambda = _lambda.Function(
            self,
            "GenerateRecipeTextFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset(".build/lambda"),
            handler="service.drink.handlers.handle_generate_recipe_text.lambda_handler",
            layers=[lambda_layer],
            timeout=Duration.seconds(60),
            memory_size=256,
            environment={
                "RECIPES_BUCKET": recipes_bucket.bucket_name,
                "BEDROCK_TEXT_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",
            },
        )

        # Conceder permissões para a função Lambda acessar o bucket S3 e o Bedrock
        recipes_bucket.grant_write(self.generate_recipe_text_lambda)
        self.generate_recipe_text_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=["*"],  # Idealmente, restringir a ARNs específicos de modelos
            )
        )

        # Criar função Lambda para gerar a imagem da receita
        self.generate_recipe_image_lambda = _lambda.Function(
            self,
            "GenerateRecipeImageFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset(".build/lambda"),
            handler="service.drink.handlers.handle_generate_recipe_image.lambda_handler",
            layers=[lambda_layer],
            timeout=Duration.seconds(60),
            memory_size=256,
            environment={
                "RECIPES_BUCKET": recipes_bucket.bucket_name,
                "BEDROCK_IMAGE_MODEL_ID": "stability.stable-diffusion-xl-v1",
            },
        )

        # Conceder permissões para a função Lambda acessar o bucket S3 e o Bedrock
        recipes_bucket.grant_write(self.generate_recipe_image_lambda)
        self.generate_recipe_image_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=["*"],  # Idealmente, restringir a ARNs específicos de modelos
            )
        )

        # Criar função Lambda para enviar notificação
        self.send_notification_lambda = _lambda.Function(
            self,
            "SendNotificationFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset(".build/lambda"),
            handler="service.drink.handlers.handle_send_notification.lambda_handler",
            layers=[lambda_layer],
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "RECIPES_BUCKET": recipes_bucket.bucket_name,
                "SENDGRID_SECRET_NAME": sendgrid_secret.secret_name,
            },
        )

        # Conceder permissões para a função Lambda acessar o bucket S3 e o Secrets Manager
        recipes_bucket.grant_read(self.send_notification_lambda)
        sendgrid_secret.grant_read(self.send_notification_lambda)

        # Definir as tarefas do Step Functions
        persist_task = tasks.LambdaInvoke(
            self,
            "PersistInitialRequest",
            lambda_function=self.persist_initial_lambda,
            output_path="$.Payload",
        )

        generate_text_task = tasks.LambdaInvoke(
            self,
            "GenerateRecipeText",
            lambda_function=self.generate_recipe_text_lambda,
            output_path="$.Payload",
        )

        generate_image_task = tasks.LambdaInvoke(
            self,
            "GenerateRecipeImage",
            lambda_function=self.generate_recipe_image_lambda,
            output_path="$.Payload",
        )

        send_notification_task = tasks.LambdaInvoke(
            self,
            "SendNotification",
            lambda_function=self.send_notification_lambda,
            output_path="$.Payload",
        )

        # Definir o fluxo do Step Functions
        workflow_definition = persist_task.next(generate_text_task).next(generate_image_task).next(send_notification_task)

        # Criar a máquina de estado do Step Functions
        self.state_machine = sfn.StateMachine(
            self,
            "DrinkRecipeStateMachine",
            definition=workflow_definition,
            timeout=Duration.minutes(5),
        )
