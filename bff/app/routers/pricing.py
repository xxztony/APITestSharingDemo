from fastapi import APIRouter

from app.clients import pricing_grpc_client
from app.models.common import success_response

router = APIRouter(tags=["pricing"])


@router.get("/pricing/{symbol}")
async def get_price(symbol: str) -> dict:
    return success_response(await pricing_grpc_client.get_price(symbol))


@router.get("/pricing/{symbol}/stream-demo")
async def stream_price_demo(symbol: str) -> dict:
    return success_response(await pricing_grpc_client.stream_price_demo(symbol))

