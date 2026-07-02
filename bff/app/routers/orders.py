from fastapi import APIRouter, Query

from app.clients import order_client
from app.models.common import success_response

router = APIRouter(tags=["orders"])


@router.get("/orders")
async def list_orders(
    accountId: str | None = Query(default=None),
    status: str | None = Query(default=None),
    product: str | None = Query(default=None),
    symbol: str | None = Query(default=None),
) -> dict:
    orders = await order_client.list_orders(account_id=accountId, status=status, product=product or symbol)
    return success_response(orders)


@router.get("/orders/{order_id}")
async def get_order(order_id: str) -> dict:
    return success_response(await order_client.get_order(order_id))


@router.post("/orders")
async def create_order(payload: dict) -> dict:
    return success_response(await order_client.create_order(payload))


@router.patch("/orders/{order_id}/cancel")
async def cancel_order(order_id: str) -> dict:
    return success_response(await order_client.cancel_order(order_id))
