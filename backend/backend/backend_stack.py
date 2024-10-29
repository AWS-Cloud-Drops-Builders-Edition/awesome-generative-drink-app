from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)
from constructs import Construct
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion

class BackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_layer = PythonLayerVersion(
            self, 
            'CommonDrinkAppLayer',
            entry='.build/layer',
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            description='Common layer for Lambda functions'
        )

        # Define the Lambda function
        greeter_lambda = _lambda.Function(
            self, 'GreeterHandler',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('.build/lambda'),
            handler='handler.handler',
            layers=[lambda_layer]
        )

        # Create an API Gateway
        api = apigw.RestApi(self, "GreeterApi")

        # Add a GET method to the API's root
        api.root.add_method(
            "GET", 
            apigw.LambdaIntegration(greeter_lambda)
        )