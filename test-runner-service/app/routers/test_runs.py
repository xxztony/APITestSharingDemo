from fastapi import APIRouter, HTTPException

from app.runner import execute_test_run, get_test_run, list_test_runs

router = APIRouter(tags=["test-runs"])


@router.post("/test-runs")
def trigger_test_run() -> dict:
    return execute_test_run()


@router.get("/test-runs")
def list_test_runs_endpoint() -> list[dict]:
    return list_test_runs()


@router.get("/test-runs/{run_id}")
def get_test_run_endpoint(run_id: str) -> dict:
    test_run = get_test_run(run_id)
    if not test_run:
        raise HTTPException(status_code=404, detail={"errorCode": "TEST_RUN_NOT_FOUND", "message": "Test run not found"})
    return test_run

