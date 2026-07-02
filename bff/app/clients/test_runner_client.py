import os
from typing import Any

import httpx

from app.models.common import ServiceError

BASE_URL = os.getenv("TEST_RUNNER_URL", "http://localhost:8004").rstrip("/")


def _decode_json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return {"raw": response.text}


async def _request(method: str, path: str, **kwargs) -> Any:
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.request(method, f"{BASE_URL}{path}", **kwargs)
    except httpx.HTTPError as exc:
        raise ServiceError("TEST_RUNNER_UNAVAILABLE", str(exc), {"service": "test-runner-service"}) from exc

    payload = _decode_json(response)
    if response.status_code >= 400:
        detail = payload.get("detail", payload) if isinstance(payload, dict) else payload
        raise ServiceError(
            "TEST_RUNNER_ERROR",
            "Test runner request failed",
            {"upstreamStatus": response.status_code, "response": detail},
            status_code=response.status_code,
        )
    return payload


async def trigger_test_run() -> dict:
    return await _request("POST", "/test-runs")


async def list_test_runs() -> list[dict]:
    return await _request("GET", "/test-runs")


async def get_test_run(run_id: str) -> dict:
    return await _request("GET", f"/test-runs/{run_id}")

