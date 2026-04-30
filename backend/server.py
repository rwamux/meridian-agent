"""FastAPI application — auth and chat endpoints."""
from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from agent import chat
from auth import AuthError, CustomerInfo, create_access_token, decode_access_token, verify_pin
from config import settings
from models import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    HealthResponse,
    LoginRequest,
    LoginResponse,
)

app = FastAPI(title="Meridian Customer Support API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_bearer = HTTPBearer()


def _get_current_customer(
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
) -> CustomerInfo:
    try:
        return decode_access_token(creds.credentials)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model=settings.model,
        mcp_url=settings.mcp_server_url,
    )


@app.post("/api/auth/login", response_model=LoginResponse)
async def login(req: LoginRequest) -> LoginResponse:
    try:
        info = await verify_pin(req.email, req.pin)
    except AuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or PIN",
        )
    token = create_access_token(info)
    return LoginResponse(
        access_token=token,
        customer_name=info.name,
        customer_id=info.customer_id,
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    customer: CustomerInfo = Depends(_get_current_customer),
) -> ChatResponse:
    history_dicts = [{"role": m.role, "content": m.content} for m in req.history]

    try:
        reply = await chat(
            message=req.message,
            history=history_dicts,
            customer_id=customer.customer_id,
            customer_email=customer.email,
            customer_name=customer.name,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent error: {exc}",
        )

    updated_history = req.history + [
        ChatMessage(role="user", content=req.message),
        ChatMessage(role="assistant", content=reply),
    ]
    return ChatResponse(response=reply, history=updated_history)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
