"""Transaction schemas for Bitpanda Developer API v1.1."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TransactionFlow = Literal["INCOMING", "OUTGOING"]


class Transaction(BaseModel):
    """Transaction data."""

    order_id: int | None = Field(
        default=None,
        description="Please use the enriched transaction if you need the orderId",
    )
    transaction_id: str = Field(json_schema_extra={"format": "uuid"})
    operation_id: str = Field(json_schema_extra={"format": "uuid"})
    asset_id: str = Field(json_schema_extra={"format": "uuid"})
    account_id: str = Field(json_schema_extra={"format": "uuid"})
    wallet_id: str = Field(json_schema_extra={"format": "uuid"})
    asset_amount: float
    fee_amount: float
    operation_type: str
    transaction_type: str | None = None
    flow: str
    credited_at: datetime
    compensates: str | None = Field(default=None, json_schema_extra={"format": "uuid"})
    trade_id: str | None = Field(default=None, json_schema_extra={"format": "uuid"})

    model_config = ConfigDict(extra="ignore")


class TransactionResponse(BaseModel):
    """Paginated response for transactions."""

    start_cursor: str | None = None
    end_cursor: str | None = None
    has_previous_page: bool | None = None
    has_next_page: bool | None = None
    page_size: int | None = None
    data: list[Transaction] | None = None
    status: int | None = None
    error: str | None = None
    message: str | None = None

    model_config = ConfigDict(extra="ignore")
