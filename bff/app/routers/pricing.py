from fastapi import APIRouter

from app.clients import pricing_grpc_client
from app.models.common import success_response

router = APIRouter(tags=["pricing"])


@router.get("/pricing/{product}")
async def get_price(product: str) -> dict:
    return success_response(await pricing_grpc_client.get_price(product))


@router.get("/pricing/{product}/stream-demo")
async def stream_price_demo(product: str) -> dict:
    return success_response(await pricing_grpc_client.stream_price_demo(product))
