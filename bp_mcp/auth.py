import os
from typing import Annotated

from fastapi import Header, HTTPException, Request
from pydantic import BaseModel


class APIKey(BaseModel):
    key: str


async def get_api_key(
    request: Request,
    authorization: Annotated[
        str | None, Header(alias="Authorization", description="Use 'Bearer <API_KEY>'")
    ] = None,
    x_api_key: Annotated[
        str | None,
        Header(alias="X-Api-Key", description="Alternative way to send Bitpanda API key"),
    ] = None,
) -> APIKey:
    """Resolve API key from headers or environment.

    The MCP bridge (mcp-remote) can pass `Authorization` and we'll parse Bearer <token>.
    We also accept `X-Api-Key` directly.
    As a last resort, you can set BITPANDA_API_KEY in the environment.
    """
    token: str | None = None

    if authorization:
        parts = authorization.split()
        # Accept either "Bearer <token>" or just raw token
        token = parts[-1] if parts else authorization
    if not token and x_api_key:
        token = x_api_key.strip()

    if not token:
        # also try process env for convenience
        token = os.getenv("BITPANDA_API_KEY")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing Bitpanda API key. Send 'Authorization: Bearer <API_KEY>' or 'X-Api-Key'.",
        )

    return APIKey(key=token)
