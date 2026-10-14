from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=100)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    # from_attributes lets Pydantic read fields off an ORM object (user.email, ...)
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    notification_preferences: dict[str, Any]
