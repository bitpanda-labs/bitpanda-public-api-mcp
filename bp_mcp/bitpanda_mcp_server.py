"""Bitpanda Public API → MCP server (via fastapi_mcp).

This FastAPI app wraps commonly used endpoints from https://developers.bitpanda.com/
 and exposes them as MCP tools using tadata-org/fastapi_mcp.

Auth:
- Provide your Bitpanda *public API* key via HTTP header `Authorization: Bearer <API_KEY>`
  (recommended for MCP clients) or `X-Api-Key: <API_KEY>`.
- Alternatively, set environment variable BITPANDA_API_KEY.

Run:
python -m bp_mcp.bitpanda_mcp_server
MCP endpoint will be available at http://localhost:8000/mcp
"""

from typing import Annotated, Literal

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Query, Request
from fastapi_mcp import FastApiMCP

from bp_mcp.auth import APIKey, get_api_key
from bp_mcp.exception_handlers import register_exception_handlers
from bp_mcp.schemas import (
    AssetWalletsData,
    AssetWalletsResponse,
    CryptoTransactionsParams,
    CryptoTransactionsResponse,
    CryptoWalletsResponse,
    FiatTransactionsParams,
    FiatTransactionsResponse,
    FiatWalletsResponse,
    PageLinks,
    PaginationMeta,
    Settings,
    TradesResponse,
)
from bp_mcp.schemas.wallets import WalletResource
from bp_mcp.utils import bp_get, get_crypto_transactions_params, get_fiat_transactions_params

# ---------------------------
# Configuration & Lifespan
# ---------------------------

# Load environment variables from a local .env file if present
load_dotenv()

settings = Settings()


app = FastAPI(
    title="Bitpanda Public API MCP",
    version="0.1.0",
    description=("Thin wrapper around Bitpanda Public API (Broker) that exposes endpoints as MCP tools."),
)
register_exception_handlers(app)


# ---------------------------
# Endpoints (wrapped as MCP tools)
# ---------------------------


# Trades — GET /trades
@app.get(
    "/bitpanda/trades",
    summary="List trades",
    tags=["Bitpanda"],
    operation_id="bitpanda_list_trades",
    response_model=TradesResponse,
)
async def list_trades(
    _: Request,
    api_key: APIKey = Depends(get_api_key),
    trade_type: Annotated[
        Literal["buy", "sell"] | None,
        Query(alias="type", description="Filter by trade type"),
    ] = None,
    cursor: Annotated[str | None, Query(description="Cursor for pagination")] = None,
    page_size: Annotated[int | None, Query(ge=1, le=500, description="Page size for pagination")] = None,
) -> TradesResponse:
    params = {
        k: v
        for k, v in {"type": trade_type, "cursor": cursor, "page_size": page_size}.items()
        if v is not None
    }
    data = await bp_get(settings, "/trades", api_key, params)
    return TradesResponse(**data)


# Asset wallets — GET /asset-wallets
@app.get(
    "/bitpanda/asset-wallets",
    summary="List asset wallets",
    tags=["Bitpanda"],
    response_model=AssetWalletsResponse,
    operation_id="bitpanda_list_asset_wallets",
)
async def list_asset_wallets(
    _: Request,
    api_key: APIKey = Depends(get_api_key),
    cursor: Annotated[str | None, Query(description="Cursor for pagination")] = None,
    page_size: Annotated[int | None, Query(ge=1, le=500, description="Page size for pagination")] = 20,
) -> AssetWalletsResponse:
    # Fetch all asset wallets from the API (no pagination support on Bitpanda side)
    data = await bp_get(settings, "/asset-wallets", api_key)

    # Extract the attributes which contain the asset wallet categories
    attributes = data.get("data", {}).get("attributes", {})

    # Flatten all asset wallets into a single list
    all_wallets = []
    for category_name, category_data in attributes.items():
        if (
            isinstance(category_data, dict)
            and "attributes" in category_data
            and "wallets" in category_data["attributes"]
        ):
            for wallet in category_data["attributes"]["wallets"]:
                wallet["category"] = category_name
                all_wallets.append(WalletResource.model_validate(wallet))
        elif isinstance(category_data, dict):  # pragma: no branch
            for subcategory_name, subcategory_data in category_data.items():
                if (  # pragma: no branch
                    isinstance(subcategory_data, dict)
                    and "attributes" in subcategory_data
                    and "wallets" in subcategory_data["attributes"]
                ):
                    for wallet in subcategory_data["attributes"]["wallets"]:
                        wallet["category"] = f"{category_name}.{subcategory_name}"
                        all_wallets.append(WalletResource.model_validate(wallet))

    # Emulate pagination
    start_index = int(cursor) if cursor else 0
    end_index = start_index + (page_size or 20)

    paginated_wallets = all_wallets[start_index:end_index]
    next_cursor = str(end_index) if end_index < len(all_wallets) else None

    return AssetWalletsResponse(
        data=AssetWalletsData.model_validate(
            {
                "type": "data",
                "attributes": {"paginated_wallets": paginated_wallets},
            }
        ),
        meta=PaginationMeta.model_validate(
            {
                "total_count": len(all_wallets),
                "page_size": page_size or 20,
                "cursor": cursor,
                "next_cursor": next_cursor,
            }
        ),
        links=PageLinks.model_validate(
            {
                "next": (
                    f"/bitpanda/asset-wallets?cursor={next_cursor}&page_size={page_size or 20}"
                    if next_cursor
                    else None
                )
            }
        ),
        last_user_action=data.get("last_user_action"),
    )


# Fiat wallets — GET /fiatwallets
@app.get(
    "/bitpanda/fiatwallets",
    summary="List fiat wallets",
    tags=["Bitpanda"],
    response_model=FiatWalletsResponse,
    operation_id="bitpanda_list_fiat_wallets",
)
async def list_fiat_wallets(
    _: Request,
    api_key: APIKey = Depends(get_api_key),
    cursor: Annotated[str | None, Query(description="Cursor for pagination")] = None,
    page_size: Annotated[int | None, Query(ge=1, le=500, description="Page size for pagination")] = 20,
) -> FiatWalletsResponse:
    # Fetch all fiat wallets from the API (no pagination support on Bitpanda side)
    data = await bp_get(settings, "/fiatwallets", api_key)
    all_wallets = data.get("data", [])

    # Emulate pagination
    start_index = int(cursor) if cursor else 0
    end_index = start_index + (page_size or 20)

    paginated_wallets = all_wallets[start_index:end_index]
    next_cursor = str(end_index) if end_index < len(all_wallets) else None

    return FiatWalletsResponse(
        data=paginated_wallets,
        meta=PaginationMeta.model_validate(
            {
                "total_count": len(all_wallets),
                "page_size": page_size or 20,
                "cursor": cursor,
                "next_cursor": next_cursor,
            }
        ),
        links=PageLinks.model_validate(
            {
                "next": (
                    f"/bitpanda/fiatwallets?cursor={next_cursor}&page_size={page_size or 20}"
                    if next_cursor
                    else None
                )
            }
        ),
        last_user_action=data.get("last_user_action"),
    )


# Fiat transactions — GET /fiatwallets/transactions
@app.get(
    "/bitpanda/fiatwallets/transactions",
    summary="List fiat transactions",
    tags=["Bitpanda"],
    response_model=FiatTransactionsResponse,
    operation_id="bitpanda_list_fiat_transactions",
)
async def list_fiat_transactions(
    _: Request,
    api_key: APIKey = Depends(get_api_key),
    params: FiatTransactionsParams = Depends(get_fiat_transactions_params),
) -> FiatTransactionsResponse:
    query_params = {
        k: v
        for k, v in {
            "type": params.transaction_type,
            "status": params.status,
            "cursor": params.cursor,
            "page_size": params.page_size,
        }.items()
        if v is not None
    }
    data = await bp_get(settings, "/fiatwallets/transactions", api_key, query_params)
    return FiatTransactionsResponse(**data)


# Crypto wallets — GET /wallets
@app.get(
    "/bitpanda/wallets",
    summary="List crypto wallets",
    tags=["Bitpanda"],
    response_model=CryptoWalletsResponse,
    operation_id="bitpanda_list_crypto_wallets",
)
async def list_crypto_wallets(
    _: Request,
    api_key: APIKey = Depends(get_api_key),
    cursor: Annotated[str | None, Query(description="Cursor for pagination")] = None,
    page_size: Annotated[int | None, Query(ge=1, le=500, description="Page size for pagination")] = 20,
) -> CryptoWalletsResponse:
    # Fetch all wallets from the API (no pagination support on Bitpanda side)
    data = await bp_get(settings, "/wallets", api_key)
    all_wallets = data.get("data", [])

    # Emulate pagination
    start_index = int(cursor) if cursor else 0
    end_index = start_index + (page_size or 20)

    paginated_wallets = all_wallets[start_index:end_index]
    next_cursor = str(end_index) if end_index < len(all_wallets) else None
    for wallet in paginated_wallets:
        wallet["category"] = "cryptocoin"

    return CryptoWalletsResponse(
        data=paginated_wallets,
        meta=PaginationMeta(
            total_count=len(all_wallets),
            page_size=page_size or 20,
            cursor=cursor,
            next_cursor=next_cursor,
        ),
        links=PageLinks(
            next=(
                f"/bitpanda/wallets?cursor={next_cursor}&page_size={page_size or 20}" if next_cursor else None
            )
        ),
        last_user_action=data.get("last_user_action"),
    )


# Crypto transactions — GET /wallets/transactions
@app.get(
    "/bitpanda/wallets/transactions",
    summary="List crypto transactions",
    tags=["Bitpanda"],
    response_model=CryptoTransactionsResponse,
    operation_id="bitpanda_list_crypto_transactions",
)
async def list_crypto_transactions(
    _: Request,
    api_key: APIKey = Depends(get_api_key),
    params: CryptoTransactionsParams = Depends(get_crypto_transactions_params),
) -> CryptoTransactionsResponse:
    query_params = {
        k: v
        for k, v in {
            "type": params.transaction_type,
            "status": params.status,
            "cursor": params.cursor,
            "page_size": params.page_size,
        }.items()
        if v is not None
    }
    data = await bp_get(settings, "/wallets/transactions", api_key, query_params)
    return CryptoTransactionsResponse(**data)


@app.get("/healthz", response_model=dict[str, str])
async def health_check() -> dict[str, str]:
    return {"status": "OK", "environment": settings.environment}


if __name__ == "__main__":  # pragma: no cover
    mcp = FastApiMCP(
        app,
        name="Bitpanda MCP",
        describe_full_response_schema=True,
        describe_all_responses=True,
    )
    mcp.mount_http()
    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104
