"""Asset schemas for Bitpanda Developer API v1.1."""

from pydantic import BaseModel, Field


class AssetData(BaseModel):
    """Asset data."""

    id: str = Field(description="The unique identifier of the asset", json_schema_extra={"format": "uuid"})
    name: str = Field(description="The name of the asset")
    symbol: str = Field(description="The symbol of the asset")


class Asset(BaseModel):
    """Asset response."""

    data: AssetData
