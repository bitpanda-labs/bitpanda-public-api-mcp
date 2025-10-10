from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .common import PageLinks, PaginationMeta, TimePoint


class TradeFeeAttributes(BaseModel):
    fee_percentage: float | None = None
    fee_amount_in_fiat: str


class TradeFee(BaseModel):
    type: Literal["fee"]
    attributes: TradeFeeAttributes


class TradeAttributes(BaseModel):
    status: str
    type: Literal["buy", "sell"]
    cryptocoin_id: str | None = None
    cryptocoin_symbol: str | None = None
    fiat_id: str | None = None
    amount_fiat: str | None = None
    amount_cryptocoin: str | None = None
    fiat_to_eur_rate: str | None = None
    wallet_id: str | None = None
    fiat_wallet_id: str | None = None
    time: TimePoint
    price: str
    is_swap: bool
    is_savings: bool | None = None
    tags: list = Field(default_factory=list)
    bfc_used: bool | None = None
    is_card: bool | None = None
    fee: TradeFee | None = None
    is_fee_transparent: bool | None = None
    model_config = ConfigDict(extra="ignore")


class TradeResource(BaseModel):
    type: Literal["trade"]
    attributes: TradeAttributes
    id: str


class TradesResponse(BaseModel):
    data: list[TradeResource]
    meta: PaginationMeta
    links: PageLinks
