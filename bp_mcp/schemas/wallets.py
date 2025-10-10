from typing import Literal

from pydantic import BaseModel, ConfigDict

from .common import PageLinks, PaginationMeta, TimePoint


class WalletAttributes(BaseModel):
    cryptocoin_id: str | None = None
    cryptocoin_symbol: str | None = None
    balance: str
    is_default: bool
    name: str
    pending_transactions_count: int
    deleted: bool
    is_index: bool
    model_config = ConfigDict(extra="ignore")


class WalletResource(BaseModel):
    category: str
    type: Literal["wallet"]
    attributes: WalletAttributes
    id: str
    model_config = ConfigDict(extra="ignore")


class CollectionAttributes(BaseModel):
    wallets: list[WalletResource]


class CollectionResource(BaseModel):
    type: Literal["collection"]
    attributes: CollectionAttributes


class AssetWalletsDataAttributes(BaseModel):
    cryptocoin: CollectionResource | None = None
    commodity: dict[str, CollectionResource] | None = None
    index: dict[str, CollectionResource] | None = None
    security: dict[Literal["stock", "etf", "etc", "fiat_earn", "mutual_fund"], CollectionResource] | None = (
        None
    )
    equity_security: (
        dict[
            Literal["equity_stock", "equity_etf", "equity_etc", "equity_right", "equity_complex_etf"],
            CollectionResource,
        ]
        | None
    ) = None
    model_config = ConfigDict(extra="allow")


class AssetWalletsData(BaseModel):
    type: Literal["data"]
    attributes: AssetWalletsDataAttributes


class AssetWalletsResponse(BaseModel):
    data: AssetWalletsData
    meta: PaginationMeta
    links: PageLinks
    last_user_action: TimePoint


class FiatWalletAttributes(BaseModel):
    fiat_id: str
    fiat_symbol: str
    balance: str
    name: str
    model_config = ConfigDict(extra="ignore")


class FiatWalletResource(BaseModel):
    type: str
    attributes: FiatWalletAttributes
    id: str


class FiatWalletsResponse(BaseModel):
    data: list[FiatWalletResource]
    meta: PaginationMeta
    links: PageLinks
    last_user_action: TimePoint | None = None


class CryptoWalletsResponse(BaseModel):
    data: list[WalletResource]
    meta: PaginationMeta
    links: PageLinks
    last_user_action: TimePoint | None = None
