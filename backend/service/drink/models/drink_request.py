from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class DrinkRequest(BaseModel):
    """
    Model representing a drink request with specific mood, flavor, and ingredients.

    Example:
        ```python
        drink = DrinkRequest(
            customer_name="Maria Silva",
            mood="happy",
            flavor="fruity",
            fruit=["pineapple", "mango"],
            liquids=["coconut water", "soda"],
            syrups=["simple syrup"],
            leaves=["mint"]
        )
        ```
    """

    customer_name: str = Field(..., description="Name of the person requesting the drink", min_length=1)

    mood: Literal["happy", "sad", "excited", "calm"] = Field(..., description="Mood associated with the drink")

    flavor: Literal["fruity", "citric", "sweet", "bitter", "complex"] = Field(..., description="Primary flavor profile of the drink")

    fruit: List[str] = Field(..., description="List of fruits to be used in the drink", min_length=1)

    liquids: List[str] = Field(..., description="List of liquids to be used in the drink", min_length=1)

    syrups: Optional[List[str]] = Field(default=[], description="Optional list of syrups to be used in the drink")

    leaves: Optional[List[str]] = Field(default=[], description="Optional list of leaves to be used in the drink")

    @field_validator("customer_name")
    @classmethod
    def customer_name_not_empty(cls, v):
        if v.strip() == "":
            raise ValueError("customer_name cannot be empty or contain only whitespace")
        return v
