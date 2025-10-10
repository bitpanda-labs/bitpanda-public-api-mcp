from typing import Annotated, Any, Literal

import httpx
from fastapi import HTTPException, Query

from bp_mcp.auth import APIKey
from bp_mcp.schemas import CryptoTransactionsParams, FiatTransactionsParams, Settings

HTTP_ERROR_THRESHOLD = 400


# Utility to perform GET with X-Api-Key header
async def bp_get(settings: Settings, path: str, api_key: APIKey, params: dict | None = None) -> Any:
    http_client = httpx.AsyncClient(base_url=settings.bitpanda_base_url, timeout=settings.request_timeout_s)
    headers = {"X-Api-Key": api_key.key}
    try:
        async with http_client:
            resp = await http_client.get(path, headers=headers, params=params)
    except httpx.HTTPError as err:  # pragma: no cover
        # network/timeout
        raise HTTPException(status_code=502, detail=f"Upstream error contacting Bitpanda: {err}") from err

    if resp.status_code >= HTTP_ERROR_THRESHOLD:  # pragma: no cover
        detail = resp.text
        raise HTTPException(status_code=resp.status_code, detail=f"Bitpanda API error: {detail}")
    return resp.json()


def get_fiat_transactions_params(
    transaction_type: Annotated[
        Literal["buy", "sell", "deposit", "withdrawal", "transfer", "refund"] | None,
        Query(alias="type", description="Filter by transaction type"),
    ] = None,
    status: Annotated[
        Literal["pending", "processing", "finished", "canceled"] | None,
        Query(description="Filter by status"),
    ] = None,
    cursor: Annotated[str | None, Query(description="Cursor for pagination")] = None,
    page_size: Annotated[int | None, Query(ge=1, le=500, description="Page size for pagination")] = None,
) -> FiatTransactionsParams:
    return FiatTransactionsParams(type=transaction_type, status=status, cursor=cursor, page_size=page_size)


def get_crypto_transactions_params(
    transaction_type: Annotated[
        Literal["buy", "sell", "deposit", "withdrawal", "transfer", "refund", "ico"] | None,
        Query(alias="type", description="Filter by transaction type"),
    ] = None,
    status: Annotated[
        Literal[
            "pending",
            "processing",
            "unconfirmed_transaction_out",
            "open_invitation",
            "finished",
            "canceled",
        ]
        | None,
        Query(description="Filter by status"),
    ] = None,
    cursor: Annotated[str | None, Query(description="Cursor for pagination")] = None,
    page_size: Annotated[int | None, Query(ge=1, le=500, description="Page size for pagination")] = None,
) -> CryptoTransactionsParams:
    # Use model_validate with aliases to keep type-checkers happy
    return CryptoTransactionsParams(type=transaction_type, status=status, cursor=cursor, page_size=page_size)
