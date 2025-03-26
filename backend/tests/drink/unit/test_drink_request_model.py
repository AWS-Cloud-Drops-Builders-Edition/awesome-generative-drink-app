"""
Tests for the DrinkRequest Pydantic model.

This module contains comprehensive tests for validating the behavior
of the DrinkRequest model, including field validations, serialization,
and deserialization.
"""
import pytest

pytestmark = pytest.mark.unit  # marca todos os testes neste arquivo como testes de unidade

import json

import pytest
from pydantic import ValidationError
from service.drink.models.drink_request import DrinkRequest


@pytest.fixture
def valid_drink_request_data():
    """Fixture providing valid data for creating a DrinkRequest instance."""
    return {
        "customer_name": "John Doe",
        "mood": "happy",
        "flavor": "fruity",
        "fruit": ["apple", "banana"],
        "liquids": ["water", "juice"],
        "syrups": ["honey"],
        "leaves": ["mint"],
    }


@pytest.fixture
def minimal_drink_request_data():
    """Fixture providing minimal valid data for creating a DrinkRequest instance."""
    return {"customer_name": "Jane Smith", "mood": "calm", "flavor": "sweet", "fruit": ["strawberry"], "liquids": ["milk"]}


def assert_validation_error(exc_info, field: str, expected_type: str = None):
    """Helper function to assert validation error details."""
    errors = exc_info.value.errors()
    field_errors = [e for e in errors if e["loc"][0] == field]
    assert field_errors, f"Expected validation error for field '{field}'"

    if expected_type:
        assert any(e["type"] == expected_type for e in field_errors), f"Expected error type '{expected_type}' for field '{field}'"


# Tests for customer_name field validation


def test_empty_customer_name(minimal_drink_request_data):
    """Test that empty customer name is rejected."""
    data = minimal_drink_request_data.copy()
    data["customer_name"] = ""

    with pytest.raises(ValidationError) as exc_info:
        DrinkRequest(**data)

    assert_validation_error(exc_info, "customer_name", "string_too_short")


def test_whitespace_customer_name(minimal_drink_request_data):
    """Test that whitespace-only customer name is rejected."""
    data = minimal_drink_request_data.copy()
    data["customer_name"] = "   "

    with pytest.raises(ValidationError) as exc_info:
        DrinkRequest(**data)

    assert_validation_error(exc_info, "customer_name", "value_error")


# Tests for successful creation of DrinkRequest instances


def test_create_with_all_fields(valid_drink_request_data):
    """Test creating a DrinkRequest with all fields populated."""
    drink_request = DrinkRequest(**valid_drink_request_data)

    assert drink_request.model_dump() == valid_drink_request_data


def test_create_with_minimal_fields(minimal_drink_request_data):
    """Test creating a DrinkRequest with only required fields."""
    drink_request = DrinkRequest(**minimal_drink_request_data)

    expected_data = minimal_drink_request_data.copy()
    expected_data["syrups"] = []  # Default empty list
    expected_data["leaves"] = []  # Default empty list

    assert drink_request.model_dump() == expected_data


def test_create_with_empty_optional_lists(valid_drink_request_data):
    """Test creating a DrinkRequest with empty optional lists."""
    data = valid_drink_request_data.copy()
    data["syrups"] = []
    data["leaves"] = []

    drink_request = DrinkRequest(**data)
    assert drink_request.model_dump() == data


# Tests for the mood field validation


@pytest.mark.parametrize("mood_value", ["happy", "sad", "excited", "calm"])
def test_valid_mood_values(minimal_drink_request_data, mood_value):
    """Test that valid mood values are accepted."""
    data = minimal_drink_request_data.copy()
    data["mood"] = mood_value

    drink_request = DrinkRequest(**data)
    assert drink_request.mood == mood_value


def test_invalid_mood_value(minimal_drink_request_data):
    """Test that invalid mood values are rejected."""
    data = minimal_drink_request_data.copy()
    data["mood"] = "angry"  # Not in allowed values

    with pytest.raises(ValidationError) as exc_info:
        DrinkRequest(**data)

    assert_validation_error(exc_info, "mood", "literal_error")


def test_missing_mood(minimal_drink_request_data):
    """Test that missing mood field raises validation error."""
    data = minimal_drink_request_data.copy()
    del data["mood"]

    with pytest.raises(ValidationError) as exc_info:
        DrinkRequest(**data)

    assert_validation_error(exc_info, "mood", "missing")


# Tests for the flavor field validation


@pytest.mark.parametrize("flavor_value", ["fruity", "citric", "sweet", "bitter", "complex"])
def test_valid_flavor_values(minimal_drink_request_data, flavor_value):
    """Test that valid flavor values are accepted."""
    data = minimal_drink_request_data.copy()
    data["flavor"] = flavor_value

    drink_request = DrinkRequest(**data)
    assert drink_request.flavor == flavor_value


def test_invalid_flavor_value(minimal_drink_request_data):
    """Test that invalid flavor values are rejected."""
    data = minimal_drink_request_data.copy()
    data["flavor"] = "spicy"  # Not in allowed values

    with pytest.raises(ValidationError) as exc_info:
        DrinkRequest(**data)

    assert_validation_error(exc_info, "flavor", "literal_error")


def test_missing_flavor(minimal_drink_request_data):
    """Test that missing flavor field raises validation error."""
    data = minimal_drink_request_data.copy()
    del data["flavor"]

    with pytest.raises(ValidationError) as exc_info:
        DrinkRequest(**data)

    assert_validation_error(exc_info, "flavor", "missing")


# Tests for the fruit field validation


def test_valid_fruit_list(minimal_drink_request_data):
    """Test that valid fruit list is accepted."""
    data = minimal_drink_request_data.copy()
    data["fruit"] = ["apple", "orange", "banana"]

    drink_request = DrinkRequest(**data)
    assert drink_request.fruit == data["fruit"]


def test_empty_fruit_list(minimal_drink_request_data):
    """Test that empty fruit list is rejected."""
    data = minimal_drink_request_data.copy()
    data["fruit"] = []

    with pytest.raises(ValidationError) as exc_info:
        DrinkRequest(**data)

    assert_validation_error(exc_info, "fruit", "too_short")


def test_missing_fruit(minimal_drink_request_data):
    """Test that missing fruit field raises validation error."""
    data = minimal_drink_request_data.copy()
    del data["fruit"]

    with pytest.raises(ValidationError) as exc_info:
        DrinkRequest(**data)

    assert_validation_error(exc_info, "fruit", "missing")


# Tests for the liquids field validation


def test_valid_liquids_list(minimal_drink_request_data):
    """Test that valid liquids list is accepted."""
    data = minimal_drink_request_data.copy()
    data["liquids"] = ["water", "juice", "soda"]

    drink_request = DrinkRequest(**data)
    assert drink_request.liquids == data["liquids"]


def test_empty_liquids_list(minimal_drink_request_data):
    """Test that empty liquids list is rejected."""
    data = minimal_drink_request_data.copy()
    data["liquids"] = []

    with pytest.raises(ValidationError) as exc_info:
        DrinkRequest(**data)

    assert_validation_error(exc_info, "liquids", "too_short")


def test_missing_liquids(minimal_drink_request_data):
    """Test that missing liquids field raises validation error."""
    data = minimal_drink_request_data.copy()
    del data["liquids"]

    with pytest.raises(ValidationError) as exc_info:
        DrinkRequest(**data)

    assert_validation_error(exc_info, "liquids", "missing")


# Tests for the optional fields (syrups and leaves)


def test_valid_syrups_list(minimal_drink_request_data):
    """Test that valid syrups list is accepted."""
    data = minimal_drink_request_data.copy()
    data["syrups"] = ["honey", "maple"]

    drink_request = DrinkRequest(**data)
    assert drink_request.syrups == data["syrups"]


def test_valid_leaves_list(minimal_drink_request_data):
    """Test that valid leaves list is accepted."""
    data = minimal_drink_request_data.copy()
    data["leaves"] = ["mint", "basil"]

    drink_request = DrinkRequest(**data)
    assert drink_request.leaves == data["leaves"]


def test_empty_optional_lists(minimal_drink_request_data):
    """Test that empty optional lists are accepted."""
    data = minimal_drink_request_data.copy()
    data["syrups"] = []
    data["leaves"] = []

    drink_request = DrinkRequest(**data)
    assert drink_request.syrups == []
    assert drink_request.leaves == []


def test_missing_optional_fields(minimal_drink_request_data):
    """Test that missing optional fields use default values."""
    # Fields are already missing in minimal_drink_request_data
    drink_request = DrinkRequest(**minimal_drink_request_data)
    assert drink_request.syrups == []
    assert drink_request.leaves == []


# Tests for serialization and deserialization


def test_to_json(valid_drink_request_data):
    """Test conversion of DrinkRequest to JSON."""
    drink_request = DrinkRequest(**valid_drink_request_data)
    json_data = drink_request.model_dump_json()

    # Parse the JSON string back to a dict for comparison
    parsed_data = json.loads(json_data)
    assert parsed_data == valid_drink_request_data


def test_from_json(valid_drink_request_data):
    """Test creation of DrinkRequest from JSON."""
    json_data = json.dumps(valid_drink_request_data)
    drink_request = DrinkRequest.model_validate_json(json_data)

    assert drink_request.model_dump() == valid_drink_request_data


def test_string_representation(valid_drink_request_data):
    """Test string representation of DrinkRequest."""
    drink_request = DrinkRequest(**valid_drink_request_data)
    str_repr = str(drink_request)

    # Check that the string representation contains key field values
    assert valid_drink_request_data["customer_name"] in str_repr
    assert valid_drink_request_data["mood"] in str_repr
    assert valid_drink_request_data["flavor"] in str_repr
