"""Error schemas for Bitpanda Developer API v1.1."""

from pydantic import BaseModel, Field


class ErrorObject(BaseModel):
    """Standard error response."""

    status: int = Field(description="HTTP status code of the error")
    error: str = Field(description="Error name")
    message: str | None = Field(default=None, description="Detailed error message")


class SingleAuthorizationError(BaseModel):
    """Single authorization error detail."""

    code: str = Field(description="A short, machine-readable code for the error")
    status: int = Field(description="HTTP status code of the error")
    title: str = Field(description="A brief, human-readable summary of the error")


class AuthorizationError(BaseModel):
    """Authorization error response."""

    errors: list[SingleAuthorizationError]
