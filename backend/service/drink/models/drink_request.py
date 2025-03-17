from typing import Optional

from pydantic import BaseModel, EmailStr


class DrinkRequest(BaseModel):
    name: str
    base_spirit: str
    flavor_profile: str
    difficulty_level: str
    email: EmailStr
    additional_notes: Optional[str] = None
