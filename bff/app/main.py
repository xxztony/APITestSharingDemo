from typing import Annotated, Any

from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth import require_authenticated_user
from app.models.common import ServiceError, error_payload, success_response
from app.routers import dashboard, orders, portfolio, pricing, test_runs
from app.tracing import configure_tracing, instrument_fastapi_app, instrument_grpc_client, instrument_httpx_client

configure_tracing("bff")
instrument_httpx_client()
instrument_grpc_client()

app = FastAPI(
    title="Trading QA BFF",
    description="Frontend-facing API gateway for the trading QA demo platform.",
    version="1.0.0",
)

instrument_fastapi_app(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ServiceError)
async def service_error_handler(_, exc: ServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(exc.error_code, exc.message, exc.details),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=error_payload("VALIDATION_ERROR", "Request validation failed", {"errors": exc.errors()}),
    )


@app.get("/api/health", tags=["health"])
def health() -> dict:
    return success_response({"status": "ok", "service": "bff"})


@app.get("/api/auth/me", tags=["auth"])
def auth_me(claims: Annotated[dict[str, Any], Depends(require_authenticated_user)]) -> dict:
    return success_response(
        {
            "userId": claims.get("sub"),
            "username": claims.get("preferred_username"),
            "name": claims.get("name"),
            "email": claims.get("email"),
            "roles": claims.get("realm_access", {}).get("roles", []),
        }
    )


protected = [Depends(require_authenticated_user)]
app.include_router(dashboard.router, prefix="/api", dependencies=protected)
app.include_router(orders.router, prefix="/api", dependencies=protected)
app.include_router(portfolio.router, prefix="/api", dependencies=protected)
app.include_router(pricing.router, prefix="/api", dependencies=protected)
app.include_router(test_runs.router, prefix="/api", dependencies=protected)
