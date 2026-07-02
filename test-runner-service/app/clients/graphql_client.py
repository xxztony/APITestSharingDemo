import os
import time
from typing import Any

import httpx

PORTFOLIO_SERVICE_URL = os.getenv("PORTFOLIO_SERVICE_URL", "http://localhost:8002/graphql")


def _json_or_text(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text


def call_graphql(query: str, variables: dict) -> dict:
    payload = {"query": query, "variables": variables}
    started = time.perf_counter()
    response = httpx.post(PORTFOLIO_SERVICE_URL, json=payload, timeout=15.0)
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    return {
        "request_payload": payload,
        "response_status": response.status_code,
        "response_payload": _json_or_text(response),
        "duration_ms": duration_ms,
    }

