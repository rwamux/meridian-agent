"""JWT issuance/verification and MCP-backed PIN authentication."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client as streamablehttp_client

from config import settings


@dataclass
class CustomerInfo:
    customer_id: str
    name: str
    email: str
    role: str


class AuthError(Exception):
    pass


async def verify_pin(email: str, pin: str) -> CustomerInfo:
    """Call verify_customer_pin on the MCP server and return parsed customer info.

    Raises AuthError if credentials are invalid.
    """
    try:
        async with streamablehttp_client(settings.mcp_server_url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "verify_customer_pin",
                    {"email": email, "pin": str(pin)},
                )
                text = result.content[0].text if result.content else ""
    except Exception as exc:
        raise AuthError(f"MCP connection failed: {exc}") from exc

    if "Error" in text or "not found" in text.lower() or "incorrect" in text.lower():
        raise AuthError("Invalid email or PIN")

    customer_id = _extract(r"Customer ID:\s*([a-f0-9-]{36})", text)
    name = _extract(r"Customer verified:\s*(.+)", text)
    role = _extract(r"Role:\s*(\w+)", text) or "customer"

    if not customer_id:
        raise AuthError("Could not parse customer identity from MCP response")

    return CustomerInfo(customer_id=customer_id, name=name, email=email, role=role)


def _extract(pattern: str, text: str) -> str:
    m = re.search(pattern, text)
    return m.group(1).strip() if m else ""


def create_access_token(info: CustomerInfo) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiry_hours)
    payload = {
        "sub": info.customer_id,
        "email": info.email,
        "name": info.name,
        "role": info.role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> CustomerInfo:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except JWTError as exc:
        raise AuthError(f"Invalid token: {exc}") from exc

    return CustomerInfo(
        customer_id=payload["sub"],
        email=payload["email"],
        name=payload["name"],
        role=payload.get("role", "customer"),
    )
