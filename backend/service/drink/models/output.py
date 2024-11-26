from pydantic import BaseModel


class GetGreetingResponse(BaseModel):
    message: str
