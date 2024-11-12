from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel

logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver()


class GreetingResponse(BaseModel):
    message: str


@app.get("/")
@tracer.capture_method
def get_greeting():
    name = app.current_event.get_query_string_value(name="name", default_value="World")
    logger.info(f"Greeting request for name: {name}")
    return GreetingResponse(message=f"Olá, {name}")


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
