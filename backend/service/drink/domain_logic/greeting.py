from service.drink.models.input import GetGreetingRequest
from service.drink.models.output import GetGreetingResponse


def greeting(request: GetGreetingRequest) -> GetGreetingResponse:
    return GetGreetingResponse(message=f"Olá, {request.name}")
