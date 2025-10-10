from http import HTTPStatus
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


def test_health_endpoint_returns_healthy(client: TestClient) -> None:
    response = client.get("/healthz")

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["status"] == "OK"
    assert data["environment"] in {"local", "staging", "production"}


@pytest.mark.vcr
def test_get_bitpanda_trades(client: TestClient, api_key: str) -> None:
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    response = client.get("/bitpanda/trades", headers=headers)

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    # Test response structure
    assert "data" in data
    assert "meta" in data
    assert "links" in data

    # Test data array
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 10  # Based on cassette data

    # Test individual trade structure
    trade = data["data"][0]
    assert "type" in trade
    assert "attributes" in trade
    assert "id" in trade
    assert trade["type"] == "trade"

    # Test trade attributes
    attributes = trade["attributes"]
    required_attributes = [
        "status",
        "type",
        "cryptocoin_id",
        "cryptocoin_symbol",
        "fiat_id",
        "amount_fiat",
        "amount_cryptocoin",
        "fiat_to_eur_rate",
        "wallet_id",
        "fiat_wallet_id",
        "time",
        "price",
        "is_swap",
        "is_savings",
        "tags",
        "bfc_used",
        "is_card",
        "is_fee_transparent",
    ]

    for attr in required_attributes:
        assert attr in attributes, f"Missing required attribute: {attr}"

    # Test specific trade values from cassette
    assert attributes["status"] == "finished"
    assert attributes["type"] in ["buy", "sell"]
    assert isinstance(attributes["amount_fiat"], str)
    assert isinstance(attributes["amount_cryptocoin"], str)
    assert isinstance(attributes["price"], str)
    assert isinstance(attributes["is_swap"], bool)
    assert isinstance(attributes["is_savings"], bool)
    assert isinstance(attributes["bfc_used"], bool)
    assert isinstance(attributes["is_card"], bool)
    assert isinstance(attributes["is_fee_transparent"], bool)
    assert isinstance(attributes["tags"], list)

    # Test time structure
    time_obj = attributes["time"]
    assert "date_iso8601" in time_obj
    assert "unix" in time_obj
    assert isinstance(time_obj["unix"], str)

    # Test fee structure (when present)
    fee = attributes["fee"]
    assert "type" in fee
    assert "attributes" in fee
    assert "fee_percentage" in fee["attributes"]
    assert "fee_amount_in_fiat" in fee["attributes"]

    # Test metadata structure
    meta = data["meta"]
    assert "total_count" in meta
    assert "page_size" in meta
    assert "page" in meta
    assert "page_number" in meta
    assert "next_cursor" in meta

    # Test metadata values from cassette
    assert meta["total_count"] == 11
    assert meta["page_size"] == 10
    assert meta["page"] == 1
    assert meta["page_number"] == 1

    # Test links structure
    links = data["links"]
    assert "next" in links
    assert "last" in links
    assert "self" in links


@pytest.mark.vcr
def test_get_bitpanda_asset_wallets(client: TestClient, api_key: str) -> None:
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    # Test /bitpanda/asset-wallets endpoint
    response = client.get("/bitpanda/asset-wallets", headers=headers)
    assert response.status_code == HTTPStatus.OK
    data = response.json()

    # Check top-level keys
    assert "data" in data
    assert "meta" in data
    assert "links" in data
    assert "last_user_action" in data

    # Check data structure
    asset_data = data["data"]
    assert "type" in asset_data
    assert "attributes" in asset_data
    assert asset_data["type"] == "data"

    attributes = asset_data["attributes"]
    assert "paginated_wallets" in attributes
    wallets = attributes["paginated_wallets"]
    assert isinstance(wallets, list)

    # Based on cassette data, we expect multiple wallets across different categories
    assert len(wallets) > 0

    # Test wallet structure and categories
    categories_found = set()
    for wallet in wallets:
        assert "category" in wallet
        assert "id" in wallet
        assert "type" in wallet
        assert "attributes" in wallet

        # Track categories found
        categories_found.add(wallet["category"])

        # Test wallet attributes structure
        wallet_attrs = wallet["attributes"]
        required_attrs = [
            "cryptocoin_id",
            "cryptocoin_symbol",
            "balance",
            "is_default",
            "name",
            "pending_transactions_count",
            "deleted",
            "is_index",
        ]

        for attr in required_attrs:
            assert attr in wallet_attrs, f"Missing required wallet attribute: {attr}"

        # Test attribute types
        assert isinstance(wallet_attrs["cryptocoin_id"], str)
        assert isinstance(wallet_attrs["cryptocoin_symbol"], str)
        assert isinstance(wallet_attrs["balance"], str)
        assert isinstance(wallet_attrs["is_default"], bool)
        assert isinstance(wallet_attrs["name"], str)
        assert isinstance(wallet_attrs["pending_transactions_count"], int)
        assert isinstance(wallet_attrs["deleted"], bool)
        assert isinstance(wallet_attrs["is_index"], bool)

        # Test wallet type
        assert wallet["type"] == "wallet"

    # Test that we have wallets from different categories
    assert len(categories_found) > 0, (
        f"Should have wallets from at least one category, found: {categories_found}"
    )

    # Test that we have wallets with different symbols
    symbols_found = {w["attributes"]["cryptocoin_symbol"] for w in wallets}
    assert len(symbols_found) > 0, "Should have wallets with different symbols"

    # Test that we have wallets with different balances (some zero, some non-zero)
    balances = [w["attributes"]["balance"] for w in wallets]
    assert len(set(balances)) > 1, "Should have wallets with different balances"

    # Test that all wallets have valid UUIDs as IDs
    for wallet in wallets:
        wallet_id = wallet["id"]
        assert len(wallet_id) > 0, "Wallet ID should not be empty"
        assert "-" in wallet_id, "Wallet ID should be a UUID format"

    # Check meta structure
    meta = data["meta"]
    assert "total_count" in meta
    assert "page_size" in meta
    assert "cursor" in meta
    assert "next_cursor" in meta

    # Test meta values
    assert isinstance(meta["total_count"], int)
    assert meta["total_count"] > 0
    assert isinstance(meta["page_size"], int)
    assert meta["page_size"] > 0
    assert meta["cursor"] is None  # First page should have no cursor
    # next_cursor may or may not be present depending on total count vs page size

    # Check links structure
    links = data["links"]
    assert "next" in links
    assert "last" in links
    assert "self" in links

    # Test that next link is properly formatted
    assert "cursor=" in links["next"]
    assert "page_size=" in links["next"]

    # Test last_user_action structure
    last_user_action = data["last_user_action"]
    assert "date_iso8601" in last_user_action
    assert "unix" in last_user_action
    assert isinstance(last_user_action["unix"], str)
    assert isinstance(last_user_action["date_iso8601"], str)


@pytest.mark.vcr
def test_get_bitpanda_asset_wallets_pagination(
    client: TestClient, api_key: str
) -> None:
    """Test pagination functionality for asset wallets endpoint."""
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    # Test first page with small page size
    page_size = 3
    response = client.get(
        f"/bitpanda/asset-wallets?page_size={page_size}", headers=headers
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()

    # Should have wallets on first page (up to page_size)
    first_page_wallets = data["data"]["attributes"]["paginated_wallets"]
    assert len(first_page_wallets) <= page_size
    assert data["meta"]["page_size"] == page_size
    assert data["meta"]["cursor"] is None

    # If there are more wallets, test pagination
    next_cursor = data["meta"]["next_cursor"]
    response2 = client.get(
        f"/bitpanda/asset-wallets?cursor={next_cursor}&page_size={page_size}",
        headers=headers,
    )
    assert response2.status_code == HTTPStatus.OK
    data2 = response2.json()

    # Should have wallets on second page
    second_page_wallets = data2["data"]["attributes"]["paginated_wallets"]
    assert len(second_page_wallets) > 0
    assert data2["meta"]["cursor"] == next_cursor

    # Test that we get different wallets on different pages
    first_page_wallet_ids = {w["id"] for w in first_page_wallets}
    second_page_wallet_ids = {w["id"] for w in second_page_wallets}
    assert first_page_wallet_ids.isdisjoint(second_page_wallet_ids), (
        "Pages should contain different wallets"
    )


@pytest.mark.vcr
def test_get_bitpanda_fiat_wallets(client: TestClient, api_key: str) -> None:
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    response = client.get("/bitpanda/fiatwallets", headers=headers)

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    # Test response structure
    assert "data" in data
    assert "last_user_action" in data

    # Test data array structure
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0

    # Test individual fiat wallet structure
    for wallet in data["data"]:
        assert "type" in wallet
        assert "attributes" in wallet
        assert "id" in wallet
        assert wallet["type"] == "fiat_wallet"

        # Test wallet attributes structure
        attributes = wallet["attributes"]
        required_attributes = [
            "fiat_id",
            "fiat_symbol",
            "balance",
            "name",
        ]

        for attr in required_attributes:
            assert attr in attributes, f"Missing required attribute: {attr}"

        # Test attribute types
        assert isinstance(attributes["fiat_id"], str)
        assert isinstance(attributes["fiat_symbol"], str)
        assert isinstance(attributes["balance"], str)
        assert isinstance(attributes["name"], str)

        # Test wallet ID format (should be UUID)
        wallet_id = wallet["id"]
        assert len(wallet_id) > 0, "Wallet ID should not be empty"
        assert "-" in wallet_id, "Wallet ID should be a UUID format"

    # Test that we have wallets with different fiat symbols
    symbols_found = {wallet["attributes"]["fiat_symbol"] for wallet in data["data"]}
    assert len(symbols_found) > 1, "Should have wallets with different fiat symbols"

    # Test that we have wallets with different balances
    balances = [wallet["attributes"]["balance"] for wallet in data["data"]]
    assert len(set(balances)) > 1, "Should have wallets with different balances"

    # Test last_user_action structure
    last_user_action = data["last_user_action"]
    assert "date_iso8601" in last_user_action
    assert "unix" in last_user_action
    assert isinstance(last_user_action["date_iso8601"], str)
    assert isinstance(last_user_action["unix"], str)


@pytest.mark.vcr
def test_get_bitpanda_fiat_wallets_transactions(
    client: TestClient, api_key: str
) -> None:
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    response = client.get("/bitpanda/fiatwallets/transactions", headers=headers)

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    # Test response structure
    assert "data" in data
    assert "meta" in data
    assert "links" in data

    # Test data array
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 10  # Based on cassette data

    # Test individual transaction structure
    for transaction in data["data"]:
        assert "type" in transaction
        assert "attributes" in transaction
        assert "id" in transaction
        assert transaction["type"] == "fiat_wallet_transaction"

        # Test transaction attributes
        attributes = transaction["attributes"]
        required_attributes = [
            "fiat_wallet_id",
            "user_id",
            "fiat_id",
            "amount",
            "fee",
            "to_eur_rate",
            "time",
            "in_or_out",
            "type",
            "status",
            "confirmation_by",
            "confirmed",
            "requires_2fa_approval",
            "is_savings",
            "last_changed",
            "tags",
            "public_status",
            "is_index",
            "is_card",
            "is_card_order_charge",
            "is_fee_transparent",
        ]

        for attr in required_attributes:
            assert attr in attributes, f"Missing required attribute: {attr}"

    # Test metadata structure
    meta = data["meta"]
    assert "total_count" in meta
    assert "page_size" in meta
    assert "page" in meta
    assert "page_number" in meta
    assert "next_cursor" in meta

    # Test links structure
    links = data["links"]
    assert "next" in links
    assert "last" in links
    assert "self" in links


@pytest.mark.vcr
def test_get_bitpanda_list_crypto_wallets(client: TestClient, api_key: str) -> None:
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    response = client.get("/bitpanda/wallets", headers=headers)

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    # Test response structure
    assert "data" in data
    assert "last_user_action" in data

    # Test data array structure
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0

    # Test individual wallet structure
    for wallet in data["data"]:
        assert "type" in wallet
        assert "attributes" in wallet
        assert "id" in wallet
        assert wallet["type"] == "wallet"

        # Test wallet attributes structure
        attributes = wallet["attributes"]
        required_attributes = [
            "cryptocoin_id",
            "cryptocoin_symbol",
            "balance",
            "is_default",
            "name",
            "pending_transactions_count",
            "deleted",
            "is_index",
        ]

        for attr in required_attributes:
            assert attr in attributes, f"Missing required attribute: {attr}"

        # Test attribute types
        assert isinstance(attributes["cryptocoin_id"], str)
        assert isinstance(attributes["cryptocoin_symbol"], str)
        assert isinstance(attributes["balance"], str)
        assert isinstance(attributes["is_default"], bool)
        assert isinstance(attributes["name"], str)
        assert isinstance(attributes["pending_transactions_count"], int)
        assert isinstance(attributes["deleted"], bool)
        assert isinstance(attributes["is_index"], bool)

    # Test that we have wallets with different crypto symbols
    symbols_found = {
        wallet["attributes"]["cryptocoin_symbol"] for wallet in data["data"]
    }
    assert len(symbols_found) > 0, "Should have at least one crypto symbol"

    # Test that we have wallets with different balances
    balances = [wallet["attributes"]["balance"] for wallet in data["data"]]
    assert len(balances) > 0, "Should have at least one balance"

    # Test last_user_action structure
    last_user_action = data["last_user_action"]
    assert "date_iso8601" in last_user_action
    assert "unix" in last_user_action
    assert isinstance(last_user_action["date_iso8601"], str)
    assert isinstance(last_user_action["unix"], str)


@pytest.mark.vcr
def test_get_list_crypto_transactions(client: TestClient, api_key: str) -> None:
    headers = {
        "X-Api-Key": api_key,
    }
    response = client.get("/bitpanda/wallets/transactions", headers=headers)
    assert response.status_code == HTTPStatus.OK
    data = response.json()

    # Test response structure
    assert "data" in data
    assert "meta" in data
    assert "links" in data

    # Test data array structure
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0

    # Test individual transaction structure
    for transaction in data["data"]:
        assert "type" in transaction
        assert "attributes" in transaction
        assert "id" in transaction
        assert transaction["type"] == "wallet_transaction"

        # Test transaction attributes structure
        attributes = transaction["attributes"]
        required_attributes = [
            "amount",
            "time",
            "in_or_out",
            "type",
            "status",
            "wallet_id",
            "cryptocoin_id",
            "cryptocoin_symbol",
        ]

        for attr in required_attributes:
            assert attr in attributes, f"Missing required attribute: {attr}"

        # Test attribute types
        assert isinstance(attributes["amount"], str)
        assert isinstance(attributes["in_or_out"], str)
        assert isinstance(attributes["type"], str)
        assert isinstance(attributes["status"], str)
        assert isinstance(attributes["wallet_id"], str)
        assert isinstance(attributes["cryptocoin_id"], str)
        assert isinstance(attributes["cryptocoin_symbol"], str)

        # Test time structure
        time_obj = attributes["time"]
        assert "date_iso8601" in time_obj
        assert "unix" in time_obj
        assert isinstance(time_obj["date_iso8601"], str)
        assert isinstance(time_obj["unix"], str)

    # Test metadata structure
    meta = data["meta"]
    assert "total_count" in meta
    assert "page_size" in meta
    assert "page" in meta
    assert "page_number" in meta

    # Test meta types
    assert isinstance(meta["total_count"], int)
    assert isinstance(meta["page_size"], int)
    assert isinstance(meta["page"], int)
    assert isinstance(meta["page_number"], int)

    # Test links structure
    links = data["links"]
    assert "next" in links
    assert "last" in links
    assert "self" in links


def test_unhandled_exception_handler(client: TestClient) -> None:
    with patch(
        "bp_mcp.bitpanda_mcp_server.bp_get",
        side_effect=RuntimeError("Test exception for handler"),
    ):
        response = client.get(
            "/bitpanda/wallets/transactions", headers={"X-Api-Key": "test"}
        )

        # Should return 500 status code
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

        # Should return JSON with error message
        data = response.json()
        assert "error_message" in data
        assert "API unhandled exception" in data["error_message"]
        assert "Test exception for handler" in data["error_message"]
