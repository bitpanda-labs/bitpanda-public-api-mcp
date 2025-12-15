"""Bitpanda Developer API → MCP server (via fastmcp).

This FastAPI app wraps the Bitpanda Developer API from https://developer.bitpanda.com/
 and exposes endpoints as MCP tools using jlowin/fastmcp.

Auth:
- Provide your Bitpanda API key via HTTP header `X-Api-Key: <API_KEY>` (required)
  or `Authorization: Bearer <API_KEY>` (alternative).
- Alternatively, set environment variable BITPANDA_API_KEY.

Run:
python -m bp_mcp.bitpanda_mcp_server
MCP endpoint will be available at http://localhost:8000/mcp
"""

from typing import Annotated

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Query
from fastmcp import FastMCP

from bp_mcp.auth import APIKey, get_api_key
from bp_mcp.exception_handlers import register_exception_handlers
from bp_mcp.schemas import Asset, Settings, TransactionFlow, TransactionResponse, WalletResponse
from bp_mcp.utils import bp_get

# ---------------------------
# Configuration & Lifespan
# ---------------------------

# Load environment variables from a local .env file if present
load_dotenv()

settings = Settings()


app = FastAPI(
    title="Bitpanda Developer API MCP",
    version="1.1.0",
    description=("Thin wrapper around Bitpanda Developer API v1.1 that exposes endpoints as MCP tools."),
)
register_exception_handlers(app)


# ---------------------------
# Health Check
# ---------------------------


@app.get("/healthz", response_model=dict[str, str])
async def health_check() -> dict[str, str]:
    return {"status": "OK"}


# ---------------------------
# Developer API Endpoints
# ---------------------------


@app.get(
    "/v1/assets/{asset_id}",
    summary="Get asset information by asset ID",
    tags=["v1"],
    operation_id="get_asset",
    response_model=Asset,
)
async def get_asset(
    asset_id: str,
    api_key: APIKey = Depends(get_api_key),
) -> Asset:
    """Return asset information by asset id (tokenscope transaction)."""
    data = await bp_get(settings, f"/v1/assets/{asset_id}", api_key)
    return Asset(**data)


@app.get(
    "/v1/transactions",
    summary="Get paginated user transactions",
    tags=["v1"],
    operation_id="get_transactions",
    response_model=TransactionResponse,
)
async def get_transactions(  # noqa: PLR0913
    api_key: APIKey = Depends(get_api_key),
    wallet_id: Annotated[str | None, Query(description="Filter transactions by wallet ID")] = None,
    flow: Annotated[
        TransactionFlow | None, Query(description="Filter transactions by flow direction")
    ] = None,
    asset_id: Annotated[
        list[str] | None, Query(description="Filter transactions by asset identifier(s)")
    ] = None,
    from_including: Annotated[
        str | None, Query(description="Filter transactions where credited_at >= given date-time")
    ] = None,
    to_excluding: Annotated[
        str | None, Query(description="Filter transactions where credited_at < given date-time")
    ] = None,
    before: Annotated[str | None, Query(description="Return values in page before cursor")] = None,
    after: Annotated[str | None, Query(description="Return values in page after cursor")] = None,
    page_size: Annotated[int, Query(ge=1, le=100, description="Set pagination size")] = 25,
) -> TransactionResponse:
    """Return paginated response of the user's transactions (tokenscope transaction)."""
    params = {
        k: v
        for k, v in {
            "wallet_id": wallet_id,
            "flow": flow or None,
            "asset_id": asset_id,
            "from_including": from_including,
            "to_excluding": to_excluding,
            "before": before,
            "after": after,
            "page_size": page_size,
        }.items()
        if v is not None
    }
    data = await bp_get(settings, "/v1/transactions", api_key, params)
    return TransactionResponse(**data)


@app.get(
    "/v1/wallets/",
    summary="Get paginated user wallets",
    tags=["v1"],
    operation_id="get_wallets",
    response_model=WalletResponse,
)
async def get_wallets(  # noqa: PLR0913
    api_key: APIKey = Depends(get_api_key),
    asset_id: Annotated[list[str] | None, Query(description="Filter wallets by asset identifier(s)")] = None,
    index_asset_id: Annotated[
        list[str] | None, Query(description="Filter wallets by index asset identifier(s)")
    ] = None,
    last_credited_at_from_including: Annotated[
        str | None, Query(description="Filter wallets where last_credited_at >= given date-time")
    ] = None,
    last_credited_at_to_excluding: Annotated[
        str | None, Query(description="Filter wallets where last_credited_at < given date-time")
    ] = None,
    before: Annotated[str | None, Query(description="Return values in page before cursor")] = None,
    after: Annotated[str | None, Query(description="Return values in page after cursor")] = None,
    page_size: Annotated[int, Query(ge=1, le=100, description="Set pagination size")] = 25,
) -> WalletResponse:
    """Return paginated response of the user's wallets (tokenscope balance)."""
    params = {
        k: v
        for k, v in {
            "asset_id": asset_id,
            "index_asset_id": index_asset_id,
            "last_credited_at_from_including": last_credited_at_from_including,
            "last_credited_at_to_excluding": last_credited_at_to_excluding,
            "before": before,
            "after": after,
            "page_size": page_size,
        }.items()
        if v is not None
    }
    data = await bp_get(settings, "/v1/wallets/", api_key, params)
    return WalletResponse(**data)


if __name__ == "__main__":  # pragma: no cover
    mcp = FastMCP.from_fastapi(app=app)
    http_app = mcp.http_app()
    uvicorn.run(http_app, host=settings.server_host, port=settings.server_port)
