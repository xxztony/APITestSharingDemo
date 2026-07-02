from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.clients import portfolio_graphql_client
from app.models.common import success_response

router = APIRouter(tags=["portfolio"])


class RiskLimitUpdate(BaseModel):
    limit: float = Field(..., gt=0)


@router.get("/portfolio/{account_id}")
async def get_portfolio(account_id: str) -> dict:
    portfolio = await portfolio_graphql_client.get_portfolio(account_id)
    return success_response(portfolio)


@router.post("/portfolio/{account_id}/risk-limit")
async def update_risk_limit(account_id: str, payload: RiskLimitUpdate) -> dict:
    portfolio = await portfolio_graphql_client.update_risk_limit(account_id, payload.limit)
    return success_response(portfolio)

