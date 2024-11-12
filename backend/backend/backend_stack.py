from aws_cdk import Duration, Stack
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_lambda as _lambda
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from constructs import Construct


class BackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_layer = PythonLayerVersion(
            self,
            "CommonDrinkAppLayer",
            entry=".build/layer",
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            description="Common layer for Lambda functions",
        )

        greeter_lambda = _lambda.Function(
            self,
            "GreeterHandler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset(".build/lambda"),
            handler="handler.handler",
            layers=[lambda_layer],
            timeout=Duration.seconds(10),
            memory_size=128,
        )

        api = apigw.RestApi(self, "GreeterApi")

        api.root.add_method("GET", apigw.LambdaIntegration(greeter_lambda))
