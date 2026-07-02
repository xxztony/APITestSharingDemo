import asyncio
import os
import sys
from pathlib import Path

import grpc

from app.models.common import ServiceError

GENERATED_DIR = Path(__file__).resolve().parents[1] / "generated"
if str(GENERATED_DIR) not in sys.path:
    sys.path.insert(0, str(GENERATED_DIR))

import pricing_pb2  # type: ignore  # noqa: E402
import pricing_pb2_grpc  # type: ignore  # noqa: E402

HOST = os.getenv("PRICING_SERVICE_HOST", "localhost")
PORT = os.getenv("PRICING_SERVICE_PORT", "50051")


def _target() -> str:
    return f"{HOST}:{PORT}"


def _to_dict(response: pricing_pb2.PriceResponse) -> dict:
    return {
        "symbol": response.symbol,
        "bid": response.bid,
        "ask": response.ask,
        "mid": response.mid,
        "timestamp": response.timestamp,
        "source": response.source,
    }


def _service_error(exc: grpc.RpcError) -> ServiceError:
    code = exc.code()
    status_code = 404 if code == grpc.StatusCode.NOT_FOUND else 502
    return ServiceError(
        f"GRPC_{code.name}",
        exc.details() or "Pricing service request failed",
        {"grpcCode": code.name, "service": "pricing-service"},
        status_code=status_code,
    )


def _get_price_sync(symbol: str) -> dict:
    with grpc.insecure_channel(_target()) as channel:
        stub = pricing_pb2_grpc.PricingServiceStub(channel)
        try:
            response = stub.GetPrice(pricing_pb2.PriceRequest(symbol=symbol), timeout=10)
        except grpc.RpcError as exc:
            raise _service_error(exc) from exc
    return _to_dict(response)


def _stream_prices_sync(symbol: str) -> list[dict]:
    with grpc.insecure_channel(_target()) as channel:
        stub = pricing_pb2_grpc.PricingServiceStub(channel)
        try:
            responses = list(stub.StreamPrices(pricing_pb2.PriceRequest(symbol=symbol), timeout=10))
        except grpc.RpcError as exc:
            raise _service_error(exc) from exc
    return [_to_dict(response) for response in responses]


async def get_price(symbol: str) -> dict:
    return await asyncio.to_thread(_get_price_sync, symbol)


async def stream_price_demo(symbol: str) -> dict:
    updates = await asyncio.to_thread(_stream_prices_sync, symbol)
    return {"symbol": symbol.upper(), "updates": updates}

