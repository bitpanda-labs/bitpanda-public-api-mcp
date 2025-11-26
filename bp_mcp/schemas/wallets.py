"""Wallet schemas for Bitpanda Developer API v1.1."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

WalletType = Literal["STAKING", "CRYPTO_INDEX"]


class Wallet(BaseModel):
    """Wallet data."""

    wallet_id: str = Field(json_schema_extra={"format": "uuid"})
    asset_id: str = Field(json_schema_extra={"format": "uuid"})
    wallet_type: WalletType | None = None
    index_asset_id: str | None = Field(default=None, json_schema_extra={"format": "uuid"})
    last_credited_at: datetime
    balance: float

    model_config = ConfigDict(extra="ignore")


class WalletResponse(BaseModel):
    """Paginated response for wallets."""

    start_cursor: str | None = None
    end_cursor: str | None = None
    has_previous_page: bool | None = None
    has_next_page: bool | None = None
    page_size: int | None = None
    data: list[Wallet] | None = None
    status: int | None = None
    error: str | None = None
    message: str | None = None

    model_config = ConfigDict(extra="ignore")
