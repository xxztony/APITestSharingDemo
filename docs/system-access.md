# Local System Access

This page is the access sheet for the local Trading QA API Demo environment. All credentials are demo-only and must not be reused outside this workstation.

## User interfaces

| System | URL | Username | Password | Notes |
| --- | --- | --- | --- | --- |
| Trading frontend | http://localhost:3000 | `qa.user` | `qa123456` | Normal QA user, realm role `qa_user` |
| Trading frontend | http://localhost:3000 | `qa.admin` | `admin123456` | Admin demo user, roles `qa_user`, `qa_admin` |
| Keycloak admin | http://localhost:8180/admin/ | `admin` | `admin` | Realm: `trading-demo` |
| ReportPortal | http://localhost:8080 | `superadmin` | `erebus` | Project: `superadmin_personal` |
| Jaeger | http://localhost:16686 | None | None | Select a service to inspect traces |

## APIs and developer tools

| System | URL | Authentication |
| --- | --- | --- |
| BFF OpenAPI | http://localhost:8000/docs | Keycloak bearer token for `/api/*` |
| Order service OpenAPI | http://localhost:8001/docs | None on direct service access |
| Portfolio GraphQL | http://localhost:8002/graphql | None on direct service access |
| Pricing gRPC | `localhost:50051` | None; server reflection enabled |
| Test runner OpenAPI | http://localhost:8004/docs | None on direct service access |
| Keycloak realm | http://localhost:8180/realms/trading-demo | Public realm metadata |
| Keycloak token endpoint | http://localhost:8180/realms/trading-demo/protocol/openid-connect/token | Client `trading-demo-tests`, user credentials above |
| Jaeger OTLP gRPC | `localhost:4317` | None |
| Jaeger OTLP HTTP | `localhost:4318` | None |

## Data stores

| System | Host / database | Username | Password |
| --- | --- | --- | --- |
| MySQL application user | `localhost:3306/trading_demo` | `demo_user` | `demo_password` |
| MySQL root | `localhost:3306/trading_demo` | `root` | `root_password` |
| MongoDB | `mongodb://localhost:27017/qa_results` | None | None |

## Integration identifiers

| Integration | Value |
| --- | --- |
| Keycloak realm | `trading-demo` |
| Frontend OIDC client | `trading-demo-frontend` (public, Authorization Code + PKCE) |
| Pytest OIDC client | `trading-demo-tests` (public, Direct Access Grant for the demo) |
| ReportPortal project | `superadmin_personal` |
| Main source repository | https://github.com/xxztony/APITestSharingDemo |
| Standalone test repository | https://github.com/xxztony/APITestAutomationFramework |

ReportPortal API keys are intentionally excluded from this document and Git. Create one under **Profile > API Keys** and expose it as `RP_API_KEY` only for the test process.

