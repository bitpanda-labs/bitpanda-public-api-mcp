import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    bitpanda_base_url: str = Field(
        default_factory=lambda: os.environ["BITPANDA_BASE_URL"],
        description="Base URL for Bitpanda Public API (override with BITPANDA_BASE_URL).",
    )
    request_timeout_s: float = Field(default=30.0, ge=1, le=120)
    server_host: str = Field(
        default_factory=lambda: os.environ["SERVER_HOST"],
        description="Host address to bind the server (override with SERVER_HOST).",
    )
    server_port: int = Field(
        default_factory=lambda: int(os.environ["SERVER_PORT"]),
        description="Port to bind the server (override with SERVER_PORT).",
    )
