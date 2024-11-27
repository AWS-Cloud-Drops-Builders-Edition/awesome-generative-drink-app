from service.drink.domain_logic.greeting import greeting
from service.drink.models.input import GetGreetingRequest
from service.drink.models.output import GetGreetingResponse


def test_greeting_with_name():
    request = GetGreetingRequest(name="John")
    response = greeting(request)
    assert isinstance(response, GetGreetingResponse)
    assert response.message == "Olá, John"


def test_greeting_with_special_chars():
    request = GetGreetingRequest(name="João!")
    response = greeting(request)
    assert isinstance(response, GetGreetingResponse)
    assert response.message == "Olá, João!"
