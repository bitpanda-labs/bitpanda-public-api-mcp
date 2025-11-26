"""Tests for authentication module."""

from http import HTTPStatus
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


def test_auth_missing_api_key(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that missing API key returns 401 error."""
    # Clear any environment variable
    monkeypatch.delenv("BITPANDA_API_KEY", raising=False)

    # No headers provided and no env variable - use protected endpoint
    response = client.get("/v1/transactions")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    data = response.json()
    assert "errors" in data
    assert data["errors"][0]["code"] == "unauthorized"
    assert "Missing Bitpanda API key" in data["errors"][0]["title"]


def test_auth_empty_authorization_header(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that empty Authorization header falls back to env or returns 401."""
    monkeypatch.delenv("BITPANDA_API_KEY", raising=False)

    headers = {"Authorization": ""}
    response = client.get("/v1/transactions", headers=headers)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@patch("bp_mcp.bitpanda_mcp_server.bp_get")
def test_auth_bearer_token(
    mock_bp_get: AsyncMock,
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that Bearer token format works."""
    monkeypatch.delenv("BITPANDA_API_KEY", raising=False)
    mock_bp_get.return_value = {"data": [], "page_size": 25}

    headers = {"Authorization": "Bearer test-api-key-12345"}
    response = client.get("/v1/transactions", headers=headers)
    # Should pass auth and reach the endpoint
    assert response.status_code == HTTPStatus.OK
    # Verify bp_get was called with the correct API key
    assert mock_bp_get.call_count == 1


@patch("bp_mcp.bitpanda_mcp_server.bp_get")
def test_auth_raw_token_in_authorization(
    mock_bp_get: AsyncMock,
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that raw token in Authorization header works."""
    monkeypatch.delenv("BITPANDA_API_KEY", raising=False)
    mock_bp_get.return_value = {"data": [], "page_size": 25}

    # Just the token without "Bearer" prefix
    headers = {"Authorization": "test-api-key-raw"}
    response = client.get("/v1/transactions", headers=headers)
    assert response.status_code == HTTPStatus.OK
    assert mock_bp_get.call_count == 1


@patch("bp_mcp.bitpanda_mcp_server.bp_get")
def test_auth_x_api_key_header(
    mock_bp_get: AsyncMock,
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that X-Api-Key header works."""
    monkeypatch.delenv("BITPANDA_API_KEY", raising=False)
    mock_bp_get.return_value = {"data": [], "page_size": 25}

    headers = {"X-Api-Key": "test-api-key-xapikey"}
    response = client.get("/v1/transactions", headers=headers)
    assert response.status_code == HTTPStatus.OK
    assert mock_bp_get.call_count == 1


@patch("bp_mcp.bitpanda_mcp_server.bp_get")
def test_auth_x_api_key_with_whitespace(
    mock_bp_get: AsyncMock,
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that X-Api-Key header strips whitespace."""
    monkeypatch.delenv("BITPANDA_API_KEY", raising=False)
    mock_bp_get.return_value = {"data": [], "page_size": 25}

    headers = {"X-Api-Key": "  test-api-key-whitespace  "}
    response = client.get("/v1/transactions", headers=headers)
    assert response.status_code == HTTPStatus.OK
    assert mock_bp_get.call_count == 1


@patch("bp_mcp.bitpanda_mcp_server.bp_get")
def test_auth_environment_variable_fallback(
    mock_bp_get: AsyncMock,
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that environment variable BITPANDA_API_KEY works as fallback."""
    # Set environment variable
    monkeypatch.setenv("BITPANDA_API_KEY", "test-env-api-key")
    mock_bp_get.return_value = {"data": [], "page_size": 25}

    # No headers provided - should use env variable
    response = client.get("/v1/transactions")
    assert response.status_code == HTTPStatus.OK
    assert mock_bp_get.call_count == 1


@patch("bp_mcp.bitpanda_mcp_server.bp_get")
def test_auth_authorization_header_takes_precedence_over_env(
    mock_bp_get: AsyncMock,
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that Authorization header takes precedence over environment variable."""
    # Set environment variable
    monkeypatch.setenv("BITPANDA_API_KEY", "env-key")
    mock_bp_get.return_value = {"data": [], "page_size": 25}

    # Provide Authorization header - should use this instead of env
    headers = {"Authorization": "Bearer header-key"}
    response = client.get("/v1/transactions", headers=headers)
    assert response.status_code == HTTPStatus.OK
    assert mock_bp_get.call_count == 1


@patch("bp_mcp.bitpanda_mcp_server.bp_get")
def test_auth_x_api_key_takes_precedence_over_env(
    mock_bp_get: AsyncMock,
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that X-Api-Key header takes precedence over environment variable."""
    # Set environment variable
    monkeypatch.setenv("BITPANDA_API_KEY", "env-key")
    mock_bp_get.return_value = {"data": [], "page_size": 25}

    # Provide X-Api-Key header - should use this instead of env
    headers = {"X-Api-Key": "x-api-key-value"}
    response = client.get("/v1/transactions", headers=headers)
    assert response.status_code == HTTPStatus.OK
    assert mock_bp_get.call_count == 1
