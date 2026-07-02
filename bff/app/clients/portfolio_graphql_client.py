import os
from typing import Any

import httpx

from app.models.common import ServiceError

GRAPHQL_URL = os.getenv("PORTFOLIO_SERVICE_URL", "http://localhost:8002/graphql")

PORTFOLIO_QUERY = """
query Portfolio($accountId: String!) {
  portfolio(accountId: $accountId) {
    accountId
    cashBalance
    riskLimit
    usedLimit
    availableLimit
    positions {
      symbol
      quantity
      averagePrice
      marketValue
    }
  }
}
"""

UPDATE_RISK_LIMIT_MUTATION = """
mutation UpdateRiskLimit($accountId: String!, $limit: Float!) {
  updateRiskLimit(accountId: $accountId, limit: $limit) {
    accountId
    cashBalance
    riskLimit
    usedLimit
    availableLimit
    positions {
      symbol
      quantity
      averagePrice
      marketValue
    }
  }
}
"""


async def _post_graphql(query: str, variables: dict) -> Any:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(GRAPHQL_URL, json={"query": query, "variables": variables})
    except httpx.HTTPError as exc:
        raise ServiceError("PORTFOLIO_SERVICE_UNAVAILABLE", str(exc), {"service": "portfolio-service"}) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise ServiceError("PORTFOLIO_INVALID_RESPONSE", response.text, {"status": response.status_code}) from exc

    if response.status_code >= 400:
        raise ServiceError(
            "PORTFOLIO_HTTP_ERROR",
            "Portfolio service request failed",
            {"status": response.status_code, "response": payload},
            status_code=response.status_code,
        )

    errors = payload.get("errors")
    if errors:
        message = errors[0].get("message", "GraphQL error") if isinstance(errors[0], dict) else str(errors[0])
        raise ServiceError("GRAPHQL_ERROR", message, {"errors": errors}, status_code=400)
    return payload.get("data", {})


async def get_portfolio(account_id: str) -> dict:
    data = await _post_graphql(PORTFOLIO_QUERY, {"accountId": account_id})
    return data["portfolio"]


async def update_risk_limit(account_id: str, limit: float) -> dict:
    data = await _post_graphql(UPDATE_RISK_LIMIT_MUTATION, {"accountId": account_id, "limit": limit})
    return data["updateRiskLimit"]

