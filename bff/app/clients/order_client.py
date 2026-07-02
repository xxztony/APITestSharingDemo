import os
from typing import Any

import httpx

from app.models.common import ServiceError

BASE_URL = os.getenv("ORDER_SERVICE_URL", "http://localhost:8001").rstrip("/")


def _decode_json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return {"raw": response.text}


def _raise_upstream_error(response: httpx.Response, payload: Any) -> None:
    detail = payload.get("detail", payload) if isinstance(payload, dict) else payload
    if isinstance(detail, list):
        raise ServiceError(
            "VALIDATION_ERROR",
            "Request validation failed",
            {"errors": detail, "upstreamStatus": response.status_code},
            status_code=response.status_code,
        )
    if isinstance(detail, dict):
        raise ServiceError(
            detail.get("errorCode", "ORDER_SERVICE_ERROR"),
            detail.get("message", "Order service request failed"),
            detail.get("details", {"upstreamStatus": response.status_code}),
            status_code=response.status_code,
        )
    raise ServiceError(
        "ORDER_SERVICE_ERROR",
        str(detail),
        {"upstreamStatus": response.status_code},
        status_code=response.status_code,
    )


async def _request(method: str, path: str, **kwargs) -> Any:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.request(method, f"{BASE_URL}{path}", **kwargs)
    except httpx.HTTPError as exc:
        raise ServiceError("ORDER_SERVICE_UNAVAILABLE", str(exc), {"service": "order-service"}) from exc

    payload = _decode_json(response)
    if response.status_code >= 400:
        _raise_upstream_error(response, payload)
    return payload


async def list_orders(account_id: str | None = None, status: str | None = None, product: str | None = None) -> list[dict]:
    params = {"account_id": account_id, "status": status, "product": product}
    clean_params = {key: value for key, value in params.items() if value}
    return await _request("GET", "/orders", params=clean_params)


async def get_order(order_id: str) -> dict:
    return await _request("GET", f"/orders/{order_id}")


async def create_order(payload: dict) -> dict:
    return await _request("POST", "/orders", json=payload)


async def cancel_order(order_id: str) -> dict:
    return await _request("PATCH", f"/orders/{order_id}/cancel")
