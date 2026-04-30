from typing import Literal

from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    pin: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    customer_name: str
    customer_id: str


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    response: str


class HealthResponse(BaseModel):
    status: str
    model: str
    mcp_url: str
