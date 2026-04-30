"""Unit tests for auth module — JWT and PIN verification."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from auth import (
    AuthError,
    CustomerInfo,
    _extract,
    create_access_token,
    decode_access_token,
)


# --- helpers ---

def _sample_customer() -> CustomerInfo:
    return CustomerInfo(
        customer_id="41c2903a-f1a5-47b7-a81d-86b50ade220f",
        name="Donald Garcia",
        email="donaldgarcia@example.net",
        role="admin",
    )


# --- JWT round-trip ---

def test_jwt_round_trip():
    info = _sample_customer()
    token = create_access_token(info)
    decoded = decode_access_token(token)

    assert decoded.customer_id == info.customer_id
    assert decoded.email == info.email
    assert decoded.name == info.name
    assert decoded.role == info.role


def test_invalid_token_raises():
    with pytest.raises(AuthError):
        decode_access_token("not.a.valid.token")


def test_tampered_token_raises():
    info = _sample_customer()
    token = create_access_token(info)
    tampered = token[:-4] + "xxxx"
    with pytest.raises(AuthError):
        decode_access_token(tampered)


# --- _extract helper ---

def test_extract_customer_id():
    text = (
        "✓ Customer verified: Donald Garcia\n"
        "Customer ID: 41c2903a-f1a5-47b7-a81d-86b50ade220f\n"
        "Email: donaldgarcia@example.net\n"
        "Role: admin"
    )
    assert _extract(r"Customer ID:\s*([a-f0-9-]{36})", text) == "41c2903a-f1a5-47b7-a81d-86b50ade220f"
    assert _extract(r"Customer verified:\s*(.+)", text) == "Donald Garcia"
    assert _extract(r"Role:\s*(\w+)", text) == "admin"


def test_extract_returns_empty_on_no_match():
    assert _extract(r"NoMatch:\s*(.+)", "some text") == ""


# --- verify_pin (mocked MCP) ---

VALID_RESPONSE = (
    "✓ Customer verified: Donald Garcia\n"
    "Customer ID: 41c2903a-f1a5-47b7-a81d-86b50ade220f\n"
    "Email: donaldgarcia@example.net\n"
    "Role: admin"
)

ERROR_RESPONSE = "Error executing tool verify_customer_pin: Customer not found or PIN incorrect"


@pytest.mark.asyncio
async def test_verify_pin_success():
    from auth import verify_pin

    mock_content = MagicMock()
    mock_content.text = VALID_RESPONSE
    mock_result = MagicMock()
    mock_result.content = [mock_content]

    mock_session = AsyncMock()
    mock_session.initialize = AsyncMock()
    mock_session.call_tool = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_streams = (AsyncMock(), AsyncMock(), None)
    mock_transport = AsyncMock()
    mock_transport.__aenter__ = AsyncMock(return_value=mock_streams)
    mock_transport.__aexit__ = AsyncMock(return_value=False)

    with patch("auth.streamablehttp_client", return_value=mock_transport), \
         patch("auth.ClientSession", return_value=mock_session):
        info = await verify_pin("donaldgarcia@example.net", "7912")

    assert info.customer_id == "41c2903a-f1a5-47b7-a81d-86b50ade220f"
    assert info.name == "Donald Garcia"
    assert info.role == "admin"


@pytest.mark.asyncio
async def test_verify_pin_wrong_pin_raises():
    from auth import verify_pin

    mock_content = MagicMock()
    mock_content.text = ERROR_RESPONSE
    mock_result = MagicMock()
    mock_result.content = [mock_content]

    mock_session = AsyncMock()
    mock_session.initialize = AsyncMock()
    mock_session.call_tool = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_streams = (AsyncMock(), AsyncMock(), None)
    mock_transport = AsyncMock()
    mock_transport.__aenter__ = AsyncMock(return_value=mock_streams)
    mock_transport.__aexit__ = AsyncMock(return_value=False)

    with patch("auth.streamablehttp_client", return_value=mock_transport), \
         patch("auth.ClientSession", return_value=mock_session):
        with pytest.raises(AuthError):
            await verify_pin("donaldgarcia@example.net", "0000")
