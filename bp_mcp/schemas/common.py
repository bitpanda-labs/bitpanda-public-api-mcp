from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TagAttributes(BaseModel):
    short_name: str
    name: str


class Tags(BaseModel):
    type: Literal["tag"]
    attributes: TagAttributes


class TimePoint(BaseModel):
    date_iso8601: str
    unix: str
    model_config = ConfigDict(extra="ignore")


class PaginationMeta(BaseModel):
    total_count: int
    page_size: int
    next_cursor: str | None = None
    cursor: str | None = None
    page_number: int | None = Field(default=None, description="Page number for pagination")
    page: int | None = Field(default=None, description="Page for pagination")
    model_config = ConfigDict(extra="ignore")


class PageLinks(BaseModel):
    self: str | None = None
    next: str | None = None
    last: str | None = None
    model_config = ConfigDict(extra="ignore")


class PaginationParams(BaseModel):
    cursor: str | None = Field(default=None, description="Cursor for pagination")
    page_size: int | None = Field(default=None, ge=1, le=500, description="Page size for pagination")
