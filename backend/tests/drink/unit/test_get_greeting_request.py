import pytest
from pydantic import ValidationError
from service.drink.models.input import GetGreetingRequest


def test_valid_name():
    request = GetGreetingRequest(name="John")
    assert request.name == "John"


def test_empty_name():
    with pytest.raises(ValidationError):
        GetGreetingRequest(name="")


def test_long_name():
    with pytest.raises(ValidationError):
        GetGreetingRequest(name="a" * 101)


def test_none_name():
    with pytest.raises(ValidationError):
        GetGreetingRequest(name=None)
