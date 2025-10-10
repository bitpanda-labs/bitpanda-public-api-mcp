from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .common import PageLinks, PaginationMeta, Tags, TimePoint
from .trades import TradeResource


class FiatTransactionsParams(BaseModel):
    transaction_type: Literal["buy", "sell", "deposit", "withdrawal", "transfer", "refund"] | None = Field(
        default=None, alias="type"
    )
    status: Literal["pending", "processing", "finished", "canceled"] | None = None
    cursor: str | None = None
    page_size: int | None = Field(default=None, ge=1, le=500)


class CryptoTransactionsParams(BaseModel):
    transaction_type: (
        Literal[
            "buy",
            "sell",
            "deposit",
            "withdrawal",
            "transfer",
            "refund",
            "ico",
        ]
        | None
    ) = Field(default=None, alias="type")
    status: (
        Literal[
            "pending",
            "processing",
            "unconfirmed_transaction_out",
            "open_invitation",
            "finished",
            "canceled",
        ]
        | None
    ) = None
    cursor: str | None = None
    page_size: int | None = Field(default=None, ge=1, le=500)


class CryptoTransactionAttributes(BaseModel):
    amount: str
    recipient: str | None = None
    time: TimePoint
    confirmations: int | None = None
    in_or_out: Literal["incoming", "outgoing"]
    type: Literal[
        "buy",
        "sell",
        "deposit",
        "withdrawal",
        "transfer",
        "refund",
        "ico",
    ]
    status: Literal[
        "pending",
        "processing",
        "unconfirmed_transaction_out",
        "open_invitation",
        "finished",
        "canceled",
    ]
    amount_eur: str | None = None
    amount_eur_incl_fee: str | None = None
    wallet_id: str
    confirmation_by: str | None = None
    confirmed: bool | None = None
    cryptocoin_id: str | None = None
    cryptocoin_symbol: str | None = None
    trade: TradeResource | None = None
    last_changed: TimePoint | None = None
    fee: str | None = None
    current_fiat_id: str | None = None
    current_fiat_amount: str | None = None
    is_savings: bool | None = None
    is_metal_storage_fee: bool | None = None
    tags: list[Tags] = Field(default_factory=list)
    public_status: str | None = None
    is_bfc: bool | None = None
    is_card: bool | None = None
    model_config = ConfigDict(extra="ignore")


class CryptoTransactionResource(BaseModel):
    type: Literal["wallet_transaction"]
    attributes: CryptoTransactionAttributes
    id: str


class CryptoTransactionsResponse(BaseModel):
    data: list[CryptoTransactionResource]
    meta: PaginationMeta
    links: PageLinks


class FiatTransactionAttributes(BaseModel):
    fiat_wallet_id: str
    user_id: str
    fiat_id: str
    amount: str
    fee: str
    to_eur_rate: str
    time: TimePoint
    in_or_out: Literal["incoming", "outgoing"]
    type: Literal["buy", "sell", "deposit", "withdrawal", "transfer", "refund"]
    status: Literal["pending", "processing", "finished", "canceled"]
    confirmation_by: Literal["not_required", "user", "admin", "email"] = "not_required"
    confirmed: bool
    requires_2fa_approval: bool
    related_fiat_wallet_transaction_id: str | None = None
    is_savings: bool | None = None
    recipient: str | None = None
    from_: str | None = Field(default=None, alias="from")
    last_changed: TimePoint | None = None
    tags: list[Tags] = Field(default_factory=list)
    public_status: str | None = None
    is_index: bool | None = None
    is_card: bool | None = None
    is_card_order_charge: bool | None = None
    is_fee_transparent: bool | None = None
    model_config = ConfigDict(extra="ignore")


class FiatTransactionResource(BaseModel):
    type: Literal["fiat_wallet_transaction"]
    attributes: FiatTransactionAttributes
    id: str


class FiatTransactionsResponse(BaseModel):
    data: list[FiatTransactionResource]
    meta: PaginationMeta
    links: PageLinks
