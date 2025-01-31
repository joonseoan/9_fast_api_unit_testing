from pydantic import BaseModel, Field


class UserPassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=3)
