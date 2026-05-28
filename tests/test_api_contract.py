"""API contract checks for MVP endpoints and OpenAPI schema."""
import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend-api"))

from app.main import app


client = TestClient(app)


def test_openapi_info_has_disclaimer():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    description = schema.get("info", {}).get("description", "")
    assert "NOT financial advice" in description


def test_openapi_contains_mvp_paths():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json().get("paths", {})

    expected_paths = [
        "/api/stocks/search",
        "/api/stocks/{exchange}/{symbol}/quote",
        "/api/stocks/{exchange}/{symbol}/overview",
        "/api/stocks/{exchange}/{symbol}/financials",
        "/api/stocks/{exchange}/{symbol}/technicals",
        "/api/stocks/{exchange}/{symbol}/filings",
        "/api/watchlists/{user_id}",
        "/api/watchlists/{user_id}/{watchlist_id}/items",
    ]

    for path in expected_paths:
        assert path in paths


def test_quote_contract_schema_reference():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    quote_get = schema["paths"]["/api/stocks/{exchange}/{symbol}/quote"]["get"]
    response_schema = quote_get["responses"]["200"]["content"]["application/json"]["schema"]
    assert response_schema["$ref"].endswith("/QuoteResponse")
