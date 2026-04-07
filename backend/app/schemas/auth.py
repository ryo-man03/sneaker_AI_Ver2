# file: app/schemas/auth.py
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_name: str
