"""Integration tests: live calls to the Meridian MCP server.

These tests hit the real MCP server — run with:
    pytest tests/test_mcp_workflows.py -v

Each test opens its own connection to avoid anyio cancel-scope task issues
with shared async fixtures.
"""
import re
import pytest
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client as streamablehttp_client

MCP_URL = "https://order-mcp-74afyau24q-uc.a.run.app/mcp"
VALID_EMAIL = "donaldgarcia@example.net"
VALID_PIN = "7912"
WRONG_PIN = "0000"


async def _call(tool: str, args: dict) -> str:
    async with streamablehttp_client(MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool, args)
            return result.content[0].text if result.content else ""


async def _tool_names() -> set[str]:
    async with streamablehttp_client(MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.list_tools()
            return {t.name for t in result.tools}


# --- Tool discovery ---

@pytest.mark.asyncio
async def test_server_exposes_expected_tools():
    names = await _tool_names()
    required = {
        "list_products", "get_product", "search_products",
        "get_customer", "verify_customer_pin",
        "list_orders", "get_order", "create_order",
    }
    assert required.issubset(names), f"Missing tools: {required - names}"


# --- Authentication workflow ---

@pytest.mark.asyncio
async def test_verify_pin_valid_credentials():
    text = await _call("verify_customer_pin", {"email": VALID_EMAIL, "pin": VALID_PIN})
    assert "Customer ID:" in text
    assert "Donald Garcia" in text


@pytest.mark.asyncio
async def test_verify_pin_wrong_pin_returns_error():
    text = await _call("verify_customer_pin", {"email": VALID_EMAIL, "pin": WRONG_PIN})
    lower = text.lower()
    assert "not found" in lower or "incorrect" in lower or "error" in lower


# --- Product browsing workflow ---

@pytest.mark.asyncio
async def test_list_products_no_filter_returns_results():
    text = await _call("list_products", {})
    assert "Found" in text and "-" in text


@pytest.mark.asyncio
async def test_list_products_category_filter():
    text = await _call("list_products", {"category": "Computers"})
    assert "COM-" in text or "Computers" in text


@pytest.mark.asyncio
async def test_search_products_returns_relevant_results():
    text = await _call("search_products", {"query": "laptop"})
    assert "laptop" in text.lower()


@pytest.mark.asyncio
async def test_get_product_valid_sku():
    list_text = await _call("list_products", {"category": "Computers"})
    match = re.search(r"\[([A-Z]+-\d+)\]", list_text)
    assert match, "No SKU found in list_products response"
    sku = match.group(1)
    detail = await _call("get_product", {"sku": sku})
    assert sku in detail


@pytest.mark.asyncio
async def test_get_product_invalid_sku_returns_error():
    text = await _call("get_product", {"sku": "XXX-9999"})
    assert "not found" in text.lower() or "error" in text.lower()


# --- Order history workflow ---

@pytest.mark.asyncio
async def test_list_orders_for_customer():
    verify_text = await _call(
        "verify_customer_pin", {"email": VALID_EMAIL, "pin": VALID_PIN}
    )
    match = re.search(r"Customer ID:\s*([a-f0-9-]{36})", verify_text)
    assert match, "customer_id not found in verify response"
    customer_id = match.group(1)

    orders_text = await _call("list_orders", {"customer_id": customer_id})
    assert isinstance(orders_text, str)
