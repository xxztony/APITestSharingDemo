# IAM API Testing Demo

This example shows pytest API tests authenticating through Keycloak, calling the BFF with `requests`, refreshing access tokens, and sending test details to local ReportPortal.

## Keycloak Token Policy

Open Keycloak Admin at http://localhost:8180/admin/ and select the `trading-demo` realm.

Realm settings -> Tokens:

- Access Token Lifespan: 1 minute (short for the demo; use 5-15 minutes for normal environments)
- Revoke Refresh Token: On
- Refresh Token Max Reuse: 0

Realm settings -> Sessions:

- SSO Session Idle: 30 minutes
- SSO Session Max: 10 hours
- Client Session Idle: 30 minutes
- Client Session Max: 10 hours

The test client is `trading-demo-tests`. It uses Direct Access Grant only to make the refresh-token flow easy to demonstrate. The browser client uses Authorization Code + PKCE and does not allow Direct Access Grant.

## ReportPortal Setup

Open http://localhost:8080, then create an API key under Profile -> API Keys. Store it in the shell environment, not in Git:

```powershell
$env:RP_API_KEY = "your-reportportal-api-key"
docker compose up -d --build test-runner-service
```

The local defaults are:

- Endpoint: `http://host.docker.internal:8080` from the test container
- Project: `superadmin_personal`
- Launch: `Trading QA IAM API Demo - <run-id>`

Trigger tests from the frontend Test Runs page, or run only the IAM examples:

```powershell
docker compose exec test-runner-service pytest -q tests/test_bff_iam.py --reportportal
```

Each test logs `request.json` and `response.json` attachments. Authentication and cookie headers are redacted before reporting.

## Production Guidance

For CI jobs, prefer a confidential Keycloak client with Service Accounts and Client Credentials instead of a shared user password. Client Credentials normally has no refresh token; obtain a new short-lived access token when it expires. Keep the password/refresh-token example for teaching interactive user-session behavior.
