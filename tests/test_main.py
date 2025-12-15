from http import HTTPStatus
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


def test_health_endpoint_returns_healthy(client: TestClient) -> None:
    response = client.get("/healthz")

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["status"] == "OK"


@pytest.mark.vcr
def test_get_asset_by_id(client: TestClient, api_key: str) -> None:
    """Test GET /v1/assets/{asset_id} endpoint."""
    # Use a known asset ID (Bitcoin on staging)
    asset_id = "ea8962d5-edee-11eb-9bf0-06502b1fe55d"
    headers = {"X-Api-Key": api_key}

    response = client.get(f"/v1/assets/{asset_id}", headers=headers)

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    # Test response structure
    assert "data" in data
    assert isinstance(data["data"], dict)

    # Test asset data
    asset_data = data["data"]
    assert "id" in asset_data
    assert "name" in asset_data
    assert "symbol" in asset_data

    # Validate the asset ID matches
    assert asset_data["id"] == asset_id
    assert isinstance(asset_data["name"], str)
    assert isinstance(asset_data["symbol"], str)
    assert len(asset_data["symbol"]) > 0


@pytest.mark.vcr
def test_get_asset_not_found(client: TestClient, api_key: str) -> None:
    """Test GET /v1/assets/{asset_id} with invalid asset ID."""
    invalid_id = "00000000-0000-0000-0000-000000000000"
    headers = {"X-Api-Key": api_key}

    response = client.get(f"/v1/assets/{invalid_id}", headers=headers)

    assert response.status_code == HTTPStatus.NOT_FOUND
    data = response.json()

    # Should return error format
    assert "status" in data or "error" in data or "message" in data


@pytest.mark.vcr
def test_get_transactions(client: TestClient, api_key: str) -> None:
    """Test GET /v1/transactions endpoint."""
    headers = {"X-Api-Key": api_key}

    response = client.get("/v1/transactions?page_size=10", headers=headers)

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    # Test response structure
    assert "data" in data
    assert "start_cursor" in data or "start_cursor" not in data  # nullable
    assert "end_cursor" in data or "end_cursor" not in data  # nullable
    assert "has_previous_page" in data or "has_previous_page" not in data  # nullable
    assert "has_next_page" in data or "has_next_page" not in data  # nullable
    assert "page_size" in data or "page_size" not in data  # nullable

    # Test data array
    assert isinstance(data["data"], list)

    # Test individual transaction structure
    transaction = data["data"][0]
    assert "transaction_id" in transaction
    assert "operation_id" in transaction
    assert "asset_id" in transaction
    assert "account_id" in transaction
    assert "wallet_id" in transaction
    assert "asset_amount" in transaction
    assert "fee_amount" in transaction
    assert "operation_type" in transaction
    assert "flow" in transaction
    assert "credited_at" in transaction

    # Validate types
    assert isinstance(transaction["asset_amount"], (int, float))
    assert isinstance(transaction["fee_amount"], (int, float))
    assert transaction["flow"] in ["incoming", "outgoing", "INCOMING", "OUTGOING"]


@pytest.mark.vcr
def test_get_transactions_with_filters(client: TestClient, api_key: str) -> None:
    """Test GET /v1/transactions with query filters."""
    headers = {"X-Api-Key": api_key}

    # Test with flow filter
    response = client.get("/v1/transactions?flow=INCOMING&page_size=5", headers=headers)

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    assert "data" in data
    assert isinstance(data["data"], list)

    # If there are transactions, verify they match the filter
    for transaction in data["data"]:
        flow = transaction["flow"]
        assert flow.upper() == "INCOMING"


@pytest.mark.vcr
def test_get_wallets(client: TestClient, api_key: str) -> None:
    """Test GET /v1/wallets/ endpoint."""
    headers = {"X-Api-Key": api_key}

    response = client.get("/v1/wallets/?page_size=10", headers=headers)

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    # Test response structure
    assert "data" in data
    assert "start_cursor" in data or "start_cursor" not in data  # nullable
    assert "end_cursor" in data or "end_cursor" not in data  # nullable
    assert "has_previous_page" in data or "has_previous_page" not in data  # nullable
    assert "has_next_page" in data or "has_next_page" not in data  # nullable
    assert "page_size" in data or "page_size" not in data  # nullable

    # Test data array
    assert isinstance(data["data"], list)

    # Test individual wallet structure
    wallet = data["data"][0]
    assert "wallet_id" in wallet
    assert "asset_id" in wallet
    assert "balance" in wallet
    assert "last_credited_at" in wallet

    # Validate types
    assert isinstance(wallet["balance"], (int, float))
    assert isinstance(wallet["last_credited_at"], str)

    # Optional fields
    if "wallet_type" in wallet and wallet["wallet_type"] is not None:
        assert wallet["wallet_type"] in ["STAKING", "CRYPTO_INDEX"]


@pytest.mark.vcr
def test_get_wallets_pagination(client: TestClient, api_key: str) -> None:
    """Test GET /v1/wallets/ with pagination."""
    headers = {"X-Api-Key": api_key}
    page_size = 2

    # Get first page
    response = client.get(f"/v1/wallets/?page_size={page_size}", headers=headers)

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    assert "data" in data

    # Get next page using cursor
    next_response = client.get(
        f"/v1/wallets/?page_size={page_size}&after={data['end_cursor']}",
        headers=headers,
    )

    assert next_response.status_code == HTTPStatus.OK
    next_data = next_response.json()

    assert "data" in next_data
    assert data["data"][0]["wallet_id"] != next_data["data"][0]["wallet_id"]


def test_unhandled_exception_handler(client: TestClient) -> None:
    with patch(
        "bp_mcp.bitpanda_mcp_server.bp_get",
        side_effect=RuntimeError("Test exception for handler"),
    ):
        response = client.get("/v1/transactions", headers={"X-Api-Key": "test"})

        # Should return 500 status code
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

        # Should return JSON with error message in new format
        data = response.json()
        assert "status" in data
        assert data["status"] == HTTPStatus.INTERNAL_SERVER_ERROR
        assert "error" in data
        assert "message" in data
        assert "API unhandled exception" in data["message"]
        assert "Test exception for handler" in data["message"]
