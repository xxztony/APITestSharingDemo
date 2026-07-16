import pytest


@pytest.mark.iam
@pytest.mark.rest
def test_bff_rejects_request_without_token(iam_api_client):
    """The BFF must reject an anonymous request before routing it downstream."""
    response = iam_api_client.get("/api/dashboard", authenticate=False)

    assert response.status_code == 401
    assert response.json()["errorCode"] == "AUTH_REQUIRED"


@pytest.mark.iam
@pytest.mark.rest
def test_token_manager_authenticates_bff_request(iam_api_client):
    """The token manager obtains a Keycloak token accepted by the BFF."""
    response = iam_api_client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json()["data"]["username"] == "qa.user"
    assert "qa_user" in response.json()["data"]["roles"]


@pytest.mark.iam
@pytest.mark.rest
def test_token_manager_refreshes_before_expiry(iam_api_client, token_manager):
    """A near-expiry token is refreshed transparently before the API request."""
    first_token = token_manager.get_access_token()
    response = iam_api_client.get("/api/dashboard")
    refreshed_token = token_manager.get_access_token()

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert token_manager.refresh_count >= 1
    assert refreshed_token != first_token
