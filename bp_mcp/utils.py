from typing import Any

import httpx
from fastapi import HTTPException

from bp_mcp.auth import APIKey
from bp_mcp.schemas import Settings

HTTP_ERROR_THRESHOLD = 400


# Utility to perform GET with X-Api-Key header
async def bp_get(settings: Settings, path: str, api_key: APIKey, params: dict | None = None) -> Any:
    """Perform GET request to Bitpanda API with authentication."""
    http_client = httpx.AsyncClient(base_url=settings.bitpanda_base_url, timeout=settings.request_timeout_s)
    headers = {"X-Api-Key": api_key.key}
    try:
        async with http_client:
            resp = await http_client.get(path, headers=headers, params=params)
    except httpx.HTTPError as err:  # pragma: no cover
        # network/timeout
        raise HTTPException(status_code=502, detail=f"Upstream error contacting Bitpanda: {err}") from err

    if resp.status_code >= HTTP_ERROR_THRESHOLD:  # pragma: no cover
        try:
            error_data = resp.json()
            # Try to extract error message from different formats
            if "message" in error_data:
                detail = error_data["message"]
            elif error_data.get("errors"):
                detail = error_data["errors"][0].get("title", resp.text)
            else:
                detail = resp.text
        except Exception:
            detail = resp.text
        raise HTTPException(status_code=resp.status_code, detail=detail)
    return resp.json()
