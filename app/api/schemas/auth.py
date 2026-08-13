from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    user_id: int


class UserResponse(BaseModel):
    user_id: int
    username: str
    role: str
    full_name: Optional[str] = None
