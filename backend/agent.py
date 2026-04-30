"""Chat agent: OpenRouter LLM + Meridian MCP tools."""
from __future__ import annotations

from agents import Agent, OpenAIProvider, RunConfig, Runner, set_tracing_disabled
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams

from config import settings

set_tracing_disabled(True)

_SYSTEM_PROMPT = """\
You are Meridian's customer support assistant. You are speaking with {name} ({email}).

Your job is to help this customer with their orders and product questions. You have access \
to Meridian's live catalog and order management system through your tools.

## What you can do
- Browse and search products (list_products, search_products, get_product)
- View this customer's order history (list_orders with customer_id="{customer_id}")
- Show order details (get_order)
- Place new orders (create_order with customer_id="{customer_id}")

## Rules
- When calling list_orders or create_order, ALWAYS use customer_id="{customer_id}".
- Never show or reference other customers' data.
- For cancellations, returns, or refunds: apologize and explain these must be handled \
  by contacting support@meridian.com — you cannot perform them through this system.
- Before placing an order, confirm the items and total with the customer.
- Be friendly, concise, and professional.
- If you don't know the answer, refer the customer to contact support@meridian.com.
- If the customer asks for something outside your scope, politely explain what your capabilities are and suggest contacting support@meridian.com.
"""


def _build_run_config() -> RunConfig:
    provider = OpenAIProvider(
        base_url=settings.openrouter_base_url,
        api_key=settings.openrouter_api_key,
        use_responses=False,
    )
    return RunConfig(model_provider=provider)


def _build_mcp_server() -> MCPServerStreamableHttp:
    return MCPServerStreamableHttp(
        params=MCPServerStreamableHttpParams(url=settings.mcp_server_url),
        name="meridian-orders",
        client_session_timeout_seconds=60,
        cache_tools_list=True,
    )


async def chat(
    message: str,
    history: list[dict],
    customer_id: str,
    customer_email: str,
    customer_name: str,
) -> str:
    """Run one conversational turn and return the assistant's reply."""
    system = _SYSTEM_PROMPT.format(
        name=customer_name,
        email=customer_email,
        customer_id=customer_id,
    )

    input_messages = [
        *history,
        {"role": "user", "content": message},
    ]

    async with _build_mcp_server() as mcp:
        agent = Agent(
            name="Meridian Support",
            instructions=system,
            model=settings.model,
            mcp_servers=[mcp],
        )
        result = await Runner.run(
            agent,
            input=input_messages,
            run_config=_build_run_config(),
            max_turns=10,
        )

    return str(result.final_output)
