from contextlib import asynccontextmanager

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from app.database import Base, SessionLocal, engine, wait_for_database
from app.schema import schema
from app.service import seed_portfolios
from app.tracing import configure_tracing, instrument_fastapi_app, instrument_sqlalchemy_engine

configure_tracing("portfolio-service")
instrument_sqlalchemy_engine(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_database()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_portfolios(db)
    yield


app = FastAPI(
    title="Trading QA Portfolio Service",
    description="GraphQL API for account portfolio and risk limits.",
    version="1.0.0",
    lifespan=lifespan,
)

instrument_fastapi_app(app)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "service": "portfolio-service"}


app.include_router(GraphQLRouter(schema), prefix="/graphql")
