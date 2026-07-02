import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import grpc

GENERATED_DIR = Path(__file__).resolve().parent / "generated"
if str(GENERATED_DIR) not in sys.path:
    sys.path.insert(0, str(GENERATED_DIR))

import pricing_pb2  # type: ignore  # noqa: E402
import pricing_pb2_grpc  # type: ignore  # noqa: E402


BASE_PRICES = {
    "LME-CA": 9125.50,
    "LME-AL": 2382.25,
    "LME-ZN": 2741.80,
    "LME-NI": 18542.40,
}


def _price_response(symbol: str) -> pricing_pb2.PriceResponse:
    base_price = BASE_PRICES[symbol]
    drift = random.uniform(-base_price * 0.0015, base_price * 0.0015)
    fair = base_price + drift
    spread = max(base_price * 0.0008, 0.05)
    bid = round(fair - spread / 2, 4)
    ask = round(fair + spread / 2, 4)
    mid = round((bid + ask) / 2, 4)
    return pricing_pb2.PriceResponse(
        symbol=symbol,
        bid=bid,
        ask=ask,
        mid=mid,
        timestamp=datetime.now(timezone.utc).isoformat(),
        source="mock-lme-feed",
    )


class PricingService(pricing_pb2_grpc.PricingServiceServicer):
    def GetPrice(self, request: pricing_pb2.PriceRequest, context: grpc.ServicerContext) -> pricing_pb2.PriceResponse:
        symbol = request.symbol.upper()
        if symbol not in BASE_PRICES:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Symbol {request.symbol} not found")
        return _price_response(symbol)

    def StreamPrices(self, request: pricing_pb2.PriceRequest, context: grpc.ServicerContext):
        symbol = request.symbol.upper()
        if symbol not in BASE_PRICES:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Symbol {request.symbol} not found")
        for _ in range(5):
            yield _price_response(symbol)
            time.sleep(0.25)

