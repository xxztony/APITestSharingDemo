import os
import sys
import time
from pathlib import Path
from typing import Any

import grpc

GENERATED_DIR = Path(__file__).resolve().parents[1] / "generated"
if str(GENERATED_DIR) not in sys.path:
    sys.path.insert(0, str(GENERATED_DIR))

import pricing_pb2  # type: ignore  # noqa: E402
import pricing_pb2_grpc  # type: ignore  # noqa: E402

PRICING_SERVICE_HOST = os.getenv("PRICING_SERVICE_HOST", "localhost")
PRICING_SERVICE_PORT = os.getenv("PRICING_SERVICE_PORT", "50051")


def _target() -> str:
    return f"{PRICING_SERVICE_HOST}:{PRICING_SERVICE_PORT}"


def _to_dict(response: pricing_pb2.PriceResponse) -> dict:
    return {
        "product": response.product,
        "bid": response.bid,
        "ask": response.ask,
        "mid": response.mid,
        "timestamp": response.timestamp,
        "source": response.source,
    }


def get_price_call(product: str) -> dict[str, Any]:
    started = time.perf_counter()
    request_payload = {"product": product}
    with grpc.insecure_channel(_target()) as channel:
        stub = pricing_pb2_grpc.PricingServiceStub(channel)
        try:
            response = stub.GetPrice(pricing_pb2.PriceRequest(product=product), timeout=10)
            response_payload: Any = _to_dict(response)
            response_status: str = "OK"
            error_message = ""
        except grpc.RpcError as exc:
            response_payload = {"error": exc.details(), "grpcCode": exc.code().name}
            response_status = exc.code().name
            error_message = exc.details() or ""
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    return {
        "request_payload": request_payload,
        "response_status": response_status,
        "response_payload": response_payload,
        "duration_ms": duration_ms,
        "error_message": error_message,
    }


def stream_prices_call(product: str) -> dict[str, Any]:
    started = time.perf_counter()
    request_payload = {"product": product}
    with grpc.insecure_channel(_target()) as channel:
        stub = pricing_pb2_grpc.PricingServiceStub(channel)
        try:
            responses = [_to_dict(response) for response in stub.StreamPrices(pricing_pb2.PriceRequest(product=product), timeout=10)]
            response_status: str = "OK"
            response_payload: Any = responses
            error_message = ""
        except grpc.RpcError as exc:
            response_status = exc.code().name
            response_payload = {"error": exc.details(), "grpcCode": exc.code().name}
            error_message = exc.details() or ""
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    return {
        "request_payload": request_payload,
        "response_status": response_status,
        "response_payload": response_payload,
        "duration_ms": duration_ms,
        "error_message": error_message,
    }
