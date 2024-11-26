from service.drink.models.output import GetGreetingResponse


def greeting(name: str) -> GetGreetingResponse:
    return GetGreetingResponse(message=f"Olá, {name}")
