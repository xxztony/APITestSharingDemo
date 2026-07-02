from app.clients.graphql_client import call_graphql

PORTFOLIO_QUERY = """
query Portfolio($accountId: String!) {
  portfolio(accountId: $accountId) {
    accountId
    cashBalance
    riskLimit
    usedLimit
    availableLimit
    positions {
      product
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
    riskLimit
    availableLimit
  }
}
"""


def test_query_portfolio_for_acc001_should_return_data(record_case):
    call = call_graphql(PORTFOLIO_QUERY, {"accountId": "ACC001"})
    body = call["response_payload"]
    record_case(
        case_id="GQL-001",
        name="Query portfolio for ACC001 should return portfolio data",
        protocol="GraphQL",
        service="portfolio-service",
        endpoint="/graphql",
        method="POST",
        expected_result="portfolio.accountId is ACC001",
        actual_result=str(body),
        **call,
    )
    assert call["response_status"] == 200
    assert "errors" not in body
    assert body["data"]["portfolio"]["accountId"] == "ACC001"


def test_query_portfolio_should_include_positions(record_case):
    call = call_graphql(PORTFOLIO_QUERY, {"accountId": "ACC001"})
    positions = call["response_payload"]["data"]["portfolio"]["positions"]
    record_case(
        case_id="GQL-002",
        name="Query portfolio should include positions",
        protocol="GraphQL",
        service="portfolio-service",
        endpoint="/graphql",
        method="POST",
        expected_result="positions array is not empty",
        actual_result=str(positions),
        **call,
    )
    assert positions


def test_update_risk_limit_should_return_updated_limit(record_case):
    call = call_graphql(UPDATE_RISK_LIMIT_MUTATION, {"accountId": "ACC001", "limit": 3200000.0})
    body = call["response_payload"]
    record_case(
        case_id="GQL-003",
        name="Update risk limit should return updated risk limit",
        protocol="GraphQL",
        service="portfolio-service",
        endpoint="/graphql",
        method="POST",
        expected_result="riskLimit is 3200000",
        actual_result=str(body),
        **call,
    )
    assert call["response_status"] == 200
    assert "errors" not in body
    assert body["data"]["updateRiskLimit"]["riskLimit"] == 3200000.0


def test_update_risk_limit_with_negative_value_should_return_graphql_error(record_case):
    call = call_graphql(UPDATE_RISK_LIMIT_MUTATION, {"accountId": "ACC001", "limit": -1.0})
    body = call["response_payload"]
    record_case(
        case_id="GQL-004",
        name="Update risk limit with negative value should return GraphQL error",
        protocol="GraphQL",
        service="portfolio-service",
        endpoint="/graphql",
        method="POST",
        expected_result="GraphQL errors present",
        actual_result=str(body),
        **call,
    )
    assert call["response_status"] == 200
    assert "errors" in body


def test_query_non_existing_account_should_return_graphql_error(record_case):
    call = call_graphql(PORTFOLIO_QUERY, {"accountId": "ACC-NOT-FOUND"})
    body = call["response_payload"]
    record_case(
        case_id="GQL-005",
        name="Query non-existing account should return GraphQL error",
        protocol="GraphQL",
        service="portfolio-service",
        endpoint="/graphql",
        method="POST",
        expected_result="GraphQL errors present",
        actual_result=str(body),
        **call,
    )
    assert call["response_status"] == 200
    assert "errors" in body
