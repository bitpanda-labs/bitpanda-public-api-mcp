import os
from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from bp_mcp.bitpanda_mcp_server import app


@pytest.fixture
def api_key() -> str:
    return os.environ["BITPANDA_API_KEY"]


@pytest.fixture
def application() -> FastAPI:
    return app


@pytest.fixture
def client(application: FastAPI) -> Iterator[TestClient]:
    with TestClient(application, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture(scope="module")
def vcr_config() -> dict:
    return {
        # Replace the Authorization request header with "DUMMY" in cassettes
        "filter_headers": [
            ("authorization", "DUMMY-KEY"),
            ("api-key", "DUMMY-KEY"),
            ("apikey", "DUMMY-KEY"),
            ("x-api-key", "DUMMY-KEY"),
            ("x-auth-token", "DUMMY-KEY"),
            ("auth_token", "DUMMY-KEY"),
        ],
        "ignore_localhost": True,
        "decode_compressed_response": True,
        "ignore_hosts": ["localstack", "testserver"],
        "filter_query_parameters": ["apikey", "auth_token", "api_key", "serp_api_key"],
        "record_mode": os.environ.get("TEST_CASSETTE_RECORD_MODE", "once"),
    }
