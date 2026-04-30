# Meridian Agent

AI-powered customer support chatbot for Meridian. Customers log in with their email and PIN, then chat with an agent that can browse products, view order history, and place new orders via a live MCP (Model Context Protocol) server.

## Architecture

```
Browser
  └── React SPA (Vite + TypeScript + Tailwind)
        └── FastAPI backend  (/api/*)
              ├── JWT authentication
              ├── openai-agents SDK  (Agent + Runner)
              └── MCP server  (Streamable HTTP)
                    └── Order management tools
```

The backend serves the React build as static files, so the entire app ships as a single container on a single port.

## Project Structure

```
meridian-agent/
├── Dockerfile                  # Multi-stage build (Node → Python)
├── railway.toml                # Railway deployment config
├── docker-compose.yml          # Local dev with hot-reload
│
├── backend/
│   ├── server.py               # FastAPI app, routes, auth middleware
│   ├── agent.py                # openai-agents chat function
│   ├── auth.py                 # PIN verification via MCP, JWT issue/decode
│   ├── models.py               # Pydantic request/response models
│   ├── config.py               # Pydantic settings (env vars)
│   ├── requirements.txt
│   ├── .env.example
│   └── tests/
│       ├── test_auth.py        # Unit tests for auth logic
│       └── test_mcp_workflows.py  # Integration tests against MCP server
│
├── frontend/
│   └── src/
│       ├── App.tsx             # Router + route guards
│       ├── api/client.ts       # Axios instance + API calls
│       ├── context/AuthContext.tsx  # Auth state, session persistence
│       ├── pages/
│       │   ├── Login.tsx
│       │   └── Chat.tsx
│       └── components/
│           ├── ChatWindow.tsx  # Message list + input form
│           └── Message.tsx     # Individual message bubble
│
└── infrastructure/
    └── terraform/              # AWS App Runner + ECR + CloudFront (optional)
```

## How It Works

1. **Login** — The frontend sends email + PIN to `/api/auth/login`. The backend calls the MCP server's `verify_customer_pin` tool. On success it issues a JWT containing the customer's ID, name, and email.

2. **Chat** — Each message is sent to `/api/chat` with the full conversation history. The backend creates an `openai-agents` `Agent` backed by the MCP server's tools, runs it, and returns the final response.

3. **MCP tools available to the agent:**
   - `list_products` / `search_products` / `get_product`
   - `list_orders` / `get_order`
   - `create_order`

4. **Model** — Defaults to `anthropic/claude-haiku-4-5` via [OpenRouter](https://openrouter.ai), making it easy to swap models with a single env var change.

## Local Development

### Prerequisites
- Python 3.12+
- Node.js 20+
- An [OpenRouter](https://openrouter.ai) API key

### Backend

```bash
cd backend
cp .env.example .env          # fill in OPENROUTER_API_KEY and JWT_SECRET
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                   # starts on http://localhost:5173
```

The Vite dev server proxies `/api` requests to `http://127.0.0.1:8000`.

### Docker (full stack)

```bash
docker-compose up --build
# App available at http://localhost:8000
```

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENROUTER_API_KEY` | Yes | — | OpenRouter API key |
| `JWT_SECRET` | Yes | — | Secret for signing JWTs (use a long random string) |
| `MODEL` | No | `anthropic/claude-haiku-4-5` | Any model available on OpenRouter |
| `MCP_SERVER_URL` | No | *(pre-configured)* | Meridian MCP server endpoint |
| `CORS_ORIGINS` | No | `["http://localhost:5173"]` | Allowed origins (JSON array) |

## Deployment

The app is deployed on [Railway](https://railway.app) using the root `Dockerfile`. Railway automatically redeploys on every push to `main`/`master`.

Set the following environment variables in the Railway service dashboard:
- `OPENROUTER_API_KEY`
- `JWT_SECRET`
- `CORS_ORIGINS` (set to your Railway public URL)

## Running Tests

```bash
cd backend
pip install pytest pytest-asyncio
pytest tests/
```
