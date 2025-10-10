"""Tests for authentication module."""

from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient


def test_auth_missing_api_key(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that missing API key returns 401 error."""
    # Clear any environment variable
    monkeypatch.delenv("BITPANDA_API_KEY", raising=False)

    # No headers provided and no env variable - use protected endpoint
    response = client.get("/bitpanda/trades")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert "Missing Bitpanda API key" in response.json()["detail"]


def test_auth_empty_authorization_header(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that empty Authorization header falls back to env or returns 401."""
    monkeypatch.delenv("BITPANDA_API_KEY", raising=False)

    headers = {"Authorization": ""}
    response = client.get("/bitpanda/trades", headers=headers)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
