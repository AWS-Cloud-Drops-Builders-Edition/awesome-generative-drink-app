from aws_cdk import Duration
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_stepfunctions as sfn
from constructs import Construct


class DrinkApiConstruct(Construct):
    def __init__(self, scope: Construct, construct_id: str, lambda_layer: _lambda.LayerVersion, state_machine: sfn.StateMachine, **kwargs) -> None:
        super().__init__(scope, construct_id)

        # Criar função Lambda para receber a solicitação da API
        self.create_drink_lambda = _lambda.Function(
            self,
            "CreateDrinkFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset(".build/lambda"),
            handler="service.drink.handlers.handle_create_drink.lambda_handler",
            layers=[lambda_layer],
            timeout=Duration.seconds(10),
            memory_size=128,
            environment={
                "DRINK_RECIPE_STEP_FUNCTION_ARN": state_machine.state_machine_arn,
            },
        )

        # Conceder permissões para a função Lambda iniciar o Step Functions
        state_machine.grant_start_execution(self.create_drink_lambda)

        # Criar API Gateway
        self.api = apigw.RestApi(
            self,
            "DrinkRecipeApi",
            rest_api_name="Drink Recipe API",
            description="API for generating drink recipes",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
            ),
        )

        # Adicionar recursos e métodos à API
        drinks_resource = self.api.root.add_resource("drink")
        drinks_resource.add_method("POST", apigw.LambdaIntegration(self.create_drink_lambda))
