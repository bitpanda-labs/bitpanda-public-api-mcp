## Bitpanda Developer API → MCP Server (FastAPI)

Thin FastAPI wrapper around Bitpanda Developer API that exposes endpoints as MCP tools using `fastmcp`.

- **MCP endpoint**: `http://localhost:8000/mcp`

> **Disclaimer**: This project has been partially vibe coded. While functional, some parts may not follow conventional best practices or may have been developed in a more experimental manner.

### Requirements

- **Python**: 3.11.x
- **Poetry**

### Install

Using Poetry (skips private dev extras):

```bash
poetry install
```

### Configure authentication

Bitpanda Public API key is required for all upstream calls.

Generate them from [here](https://web.bitpanda.com/my-account/apikey).

- Preferred: send `Authorization: Bearer <API_KEY>` header
- Alternative: send `X-Api-Key: <API_KEY>` header
- Fallback: set environment variable `BITPANDA_API_KEY` --> LOCAL ONLY

### Environment configuration (.env)

This project automatically loads variables from a local `.env` file using `python-dotenv`.

- Copy the example file and edit it:

```bash
cp .env.example .env
# then edit .env
```

**Required variables:**

- `BITPANDA_BASE_URL` - Base URL for Bitpanda Public API (e.g., `https://api.bitpanda.com/v1`)
- `APP_ENV` - Environment identifier (e.g., `local`, `staging`, `production`)
- `SERVER_HOST` - Host address to bind the server (default: `0.0.0.0`)
- `SERVER_PORT` - Port to bind the server (default: `8000`)

**Optional variables:**

- `BITPANDA_API_KEY` - API key for local development only (not recommended for production)

### Run the server

Run the module entrypoint to start the MCP server:

```bash
# Using Poetry
poetry run python -m bp_mcp.bitpanda_mcp_server

# Or with plain Python (after pip install / editable install)
python -m bp_mcp.bitpanda_mcp_server
```

This starts the API on `http://localhost:8000/mcp`.

### API Endpoints

All endpoints require authentication via `X-Api-Key` header and use cursor-based pagination.

- `GET /v1/assets/{asset_id}` — get asset information by ID
  - Path param: `asset_id` (UUID)
  - Returns: Asset data (id, name, symbol)

- `GET /v1/transactions` — get paginated user transactions
  - Query params: `wallet_id`, `flow` (INCOMING/OUTGOING), `asset_id[]`, `from_including`, `to_excluding`, `before`, `after`, `page_size` (1-100, default 25)
  - Returns: Paginated transactions with cursor-based navigation

- `GET /v1/wallets/` — get paginated user wallets
  - Query params: `asset_id[]`, `index_asset_id[]`, `last_credited_at_from_including`, `last_credited_at_to_excluding`, `before`, `after`, `page_size` (1-100, default 25)
  - Returns: Paginated wallets with cursor-based navigation

Example requests:

```bash
# Get asset by ID
curl -sS \
  -H "X-Api-Key: $API_KEY" \
  "http://localhost:8000/v1/assets/ea8962d5-edee-11eb-9bf0-06502b1fe55d" | jq .

# Get transactions for a specific wallet
curl -sS \
  -H "X-Api-Key: $API_KEY" \
  "http://localhost:8000/v1/transactions?wallet_id=1f0738f2-6834-6d28-8550-49d834ee5b52&page_size=50" | jq .

# Get all wallets
curl -sS \
  -H "X-Api-Key: $API_KEY" \
  "http://localhost:8000/v1/wallets/?page_size=100" | jq .
```

### MCP usage

The server exposes an MCP endpoint at `http://localhost:8000/mcp`. Most MCP clients can pass HTTP headers for auth.

#### Adding to Claude Desktop

```bash
claude mcp add bitpanda-developer-api/mcp --transport http --header "Authorization: Bearer xxxxxxxxxxxxxx"
```

#### Manual configuration

Example JSON config snippet for an http-based MCP client:

```json
{
  "mcpServers": {
    "bitpanda-developer-api": {
      "type": "http",
      "url": "http://localhost:8000/mcp",
      "headers": {
        "Authorization": "Bearer xxxxxxxxxxxxxx"
      }
    }
  }
}
```

### Configuration notes

- Upstream base URL defaults to a staging endpoint and can be overridden via `BITPANDA_BASE_URL`:

```bash
export BITPANDA_BASE_URL="https://developer.bitpanda.com"
```

- Request timeout defaults to 30s.
- Server host and port can be configured via environment variables:

```bash
export SERVER_HOST="127.0.0.1"  # Bind to localhost only
export SERVER_PORT="8080"        # Use custom port
```

### Development

Lint and type-check:

```bash
poetry run pre-commit run --all
```

### Project layout

- `bp_mcp/bitpanda_mcp_server.py` — FastAPI app + MCP mounting with Developer API v1.1 endpoints
- `bp_mcp/schemas/` — Pydantic models for requests/responses
- `bp_mcp/auth.py` — Authentication dependency (supports Bearer token and X-Api-Key)
- `bp_mcp/utils.py` — HTTP client helper for Bitpanda API requests
- `bp_mcp/exception_handlers.py` — Error handling with Developer API error format
- `tests/` — Test suite
- `pyproject.toml` — dependencies and tooling
- `ruff.toml`, `mypy.ini` — linting and typing config
