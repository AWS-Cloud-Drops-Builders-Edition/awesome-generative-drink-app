from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.parser import parse
from aws_lambda_powertools.utilities.typing import LambdaContext
from service.drink.domain_logic.greeting import greeting
from service.drink.models.input import GetGreetingRequest

logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver()


@app.get("/")
@tracer.capture_method
def handle_get_greeting():
    greeting_request = parse(event=app.current_event.query_string_parameters, model=GetGreetingRequest)
    logger.info(f"Greeting request for name: {greeting_request.name}")
    return greeting(greeting_request)


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
