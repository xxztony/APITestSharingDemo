from fastapi import APIRouter

from app.clients import test_runner_client
from app.models.common import success_response

router = APIRouter(tags=["test-runs"])


@router.post("/test-runs")
async def trigger_test_run() -> dict:
    return success_response(await test_runner_client.trigger_test_run())


@router.get("/test-runs")
async def list_test_runs() -> dict:
    return success_response(await test_runner_client.list_test_runs())


@router.get("/test-runs/{run_id}")
async def get_test_run(run_id: str) -> dict:
    return success_response(await test_runner_client.get_test_run(run_id))

