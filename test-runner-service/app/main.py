from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.mongodb import ensure_indexes
from app.routers.test_runs import router as test_runs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_indexes()
    yield


app = FastAPI(
    title="Trading QA Test Runner Service",
    description="Runs REST, GraphQL, and gRPC API regression tests and stores results in MongoDB.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "service": "test-runner-service"}


app.include_router(test_runs_router)

