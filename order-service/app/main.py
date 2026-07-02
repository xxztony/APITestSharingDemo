from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, SessionLocal, engine, wait_for_database
from app.routers.orders import router as orders_router
from app.service import seed_orders
from app.tracing import configure_tracing, instrument_fastapi_app, instrument_sqlalchemy_engine

configure_tracing("order-service")
instrument_sqlalchemy_engine(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_database()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_orders(db)
    yield


app = FastAPI(
    title="Trading QA Order Service",
    description="REST API for demo trading orders.",
    version="1.0.0",
    lifespan=lifespan,
)

instrument_fastapi_app(app)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "service": "order-service"}


app.include_router(orders_router)
