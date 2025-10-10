import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    bitpanda_base_url: str = Field(
        default_factory=lambda: os.environ["BITPANDA_BASE_URL"],
        description="Base URL for Bitpanda Public API (override with BITPANDA_BASE_URL).",
    )
    request_timeout_s: float = Field(default=30.0, ge=1, le=120)
    environment: str = Field(
        default_factory=lambda: os.environ["APP_ENV"], description="Environment for the server."
    )
