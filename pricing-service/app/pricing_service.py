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


def _price_response(product: str) -> pricing_pb2.PriceResponse:
    base_price = BASE_PRICES[product]
    drift = random.uniform(-base_price * 0.0015, base_price * 0.0015)
    fair = base_price + drift
    spread = max(base_price * 0.0008, 0.05)
    bid = round(fair - spread / 2, 4)
    ask = round(fair + spread / 2, 4)
    mid = round((bid + ask) / 2, 4)
    return pricing_pb2.PriceResponse(
        product=product,
        bid=bid,
        ask=ask,
        mid=mid,
        timestamp=datetime.now(timezone.utc).isoformat(),
        source="mock-lme-feed",
    )


class PricingService(pricing_pb2_grpc.PricingServiceServicer):
    def GetPrice(self, request: pricing_pb2.PriceRequest, context: grpc.ServicerContext) -> pricing_pb2.PriceResponse:
        product = request.product.upper()
        if product not in BASE_PRICES:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Product {request.product} not found")
        return _price_response(product)

    def StreamPrices(self, request: pricing_pb2.PriceRequest, context: grpc.ServicerContext):
        product = request.product.upper()
        if product not in BASE_PRICES:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Product {request.product} not found")
        for _ in range(5):
            yield _price_response(product)
            time.sleep(0.25)
