from service.drink.domain_logic.greeting import greeting
from service.drink.models.output import GetGreetingResponse


def test_greeting_with_name():
    result = greeting("John")
    assert isinstance(result, GetGreetingResponse)
    assert result.message == "Olá, John"


def test_greeting_with_special_chars():
    result = greeting("João!")
    assert isinstance(result, GetGreetingResponse)
    assert result.message == "Olá, João!"
