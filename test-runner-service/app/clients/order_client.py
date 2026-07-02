import os
import time
from typing import Any

import httpx

ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://localhost:8001").rstrip("/")


def _json_or_text(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text


def call_order(method: str, path: str, payload: dict | None = None) -> dict:
    started = time.perf_counter()
    response = httpx.request(method, f"{ORDER_SERVICE_URL}{path}", json=payload, timeout=15.0)
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    return {
        "request_payload": payload or {},
        "response_status": response.status_code,
        "response_payload": _json_or_text(response),
        "duration_ms": duration_ms,
    }

