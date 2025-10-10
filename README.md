## Bitpanda Public API → MCP Server (FastAPI)

Thin FastAPI wrapper around Bitpanda Public API that exposes commonly used endpoints as both REST and MCP tools using `fastapi_mcp`.

- **REST base URL (local)**: `http://localhost:8000`
- **MCP endpoint**: `http://localhost:8000/mcp`

### Requirements

- **Python**: >=3.11
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

- Set `BITPANDA_BASE_URL`.
- Set `APP_ENV`.

### Run the server

To ensure the MCP endpoint (`/mcp`) is mounted, run the module entrypoint:

```bash
# Using Poetry
poetry run python -m bp_mcp.bitpanda_mcp_server

# Or with plain Python (after pip install / editable install)
python -m bp_mcp.bitpanda_mcp_server
```

This starts the API on `http://localhost:8000`.

### REST endpoints

All endpoints require authentication as described above.

- `GET /bitpanda/trades` — list trades
  - Query: `type=buy|sell`, `cursor`, `page_size (1..500)`
- `GET /bitpanda/asset-wallets` — grouped asset wallets
- `GET /bitpanda/fiatwallets` — fiat wallets
- `GET /bitpanda/fiatwallets/transactions` — fiat transactions
  - Query: `type`, `status`, `cursor`, `page_size (1..500)`
- `GET /bitpanda/wallets` — crypto wallets (flat list)
- `GET /bitpanda/wallets/transactions` — crypto transactions
  - Query: `type`, `status`, `cursor`, `page_size (1..500)`

Example requests:

```bash
# Last 50 trades
curl -sS \
  -H "Authorization: Bearer $API_KEY" \
  "http://localhost:8000/bitpanda/trades?page_size=50" | jq .

# Crypto transactions (finished withdrawals), paginated
curl -sS \
  -H "X-Api-Key: $API_KEY" \
  "http://localhost:8000/bitpanda/wallets/transactions?type=withdrawal&status=finished&page_size=100" | jq .
```

### MCP usage

The server exposes an MCP endpoint at `http://localhost:8000/mcp`. Most MCP clients can pass HTTP headers for auth.

#### Adding to Claude Desktop

```bash
claude mcp add bitpanda-developer-api http://localhost:8000/mcp --transport http --header "Authorization: Bearer xxxxxxxxxxxxxx"
```

#### Manual configuration

Example JSON config snippet for an http-based MCP client:

```json
{
  "mcpServers": {
    "developers-api-mcp-server": {
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
export BITPANDA_BASE_URL="https://api.bitpanda.com/v1"
```

- Request timeout defaults to 30s.

### Development

Lint and type-check:

```bash
poetry run pre-commit run --all
```

### Project layout

- `bp_mcp/bitpanda_mcp_server.py` — FastAPI app + MCP mounting
- `bp_mcp/schemas/` — Pydantic models for requests/responses
- `bp_mcp/auth.py` — auth dependency
- `bp_mcp/utils.py` — HTTP helpers, query param builders
- `pyproject.toml` — dependencies and tooling
