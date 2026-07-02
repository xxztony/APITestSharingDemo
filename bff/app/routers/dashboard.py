import asyncio

from fastapi import APIRouter

from app.clients import order_client, pricing_grpc_client, test_runner_client
from app.models.common import success_response

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
async def dashboard() -> dict:
    orders_result, price_result, runs_result = await asyncio.gather(
        order_client.list_orders(),
        pricing_grpc_client.get_price("LME-CA"),
        test_runner_client.list_test_runs(),
        return_exceptions=True,
    )

    orders = orders_result if isinstance(orders_result, list) else []
    latest_price = price_result if isinstance(price_result, dict) else {"product": "LME-CA"}
    test_runs = runs_result if isinstance(runs_result, list) else []
    latest_run = test_runs[0] if test_runs else None

    metrics = {
        "totalOrders": len(orders),
        "openOrders": sum(1 for order in orders if order.get("status") in {"NEW", "ACCEPTED"}),
        "cancelledOrders": sum(1 for order in orders if order.get("status") == "CANCELLED"),
        "rejectedOrders": sum(1 for order in orders if order.get("status") == "REJECTED"),
        "totalAccounts": 3,
        "latestPriceProduct": latest_price.get("product", "LME-CA"),
        "latestTestPassRate": latest_run.get("pass_rate", 0) if latest_run else 0,
        "averageApiResponseTime": latest_run.get("average_duration_ms", 0) if latest_run else 0,
        "latestTestRunStatus": latest_run.get("status", "NO_RUN") if latest_run else "NO_RUN",
    }

    return success_response(
        {
            "metrics": metrics,
            "latestPrice": latest_price,
            "recentTestRun": latest_run,
            "upstreamHealth": {
                "orders": not isinstance(orders_result, Exception),
                "pricing": not isinstance(price_result, Exception),
                "testRunner": not isinstance(runs_result, Exception),
            },
        }
    )
