import asyncio
import os
import time
from typing import Any

import httpx
import jwt
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.common import ServiceError


IAM_ISSUER = os.getenv("IAM_ISSUER", "http://localhost:8180/realms/trading-demo")
IAM_JWKS_URL = os.getenv(
    "IAM_JWKS_URL",
    "http://localhost:8180/realms/trading-demo/protocol/openid-connect/certs",
)
IAM_CLIENT_ID = os.getenv("IAM_CLIENT_ID", "trading-demo-frontend")
JWKS_TTL_SECONDS = int(os.getenv("IAM_JWKS_TTL_SECONDS", "300"))

bearer_scheme = HTTPBearer(auto_error=False)

_jwks: dict[str, Any] | None = None
_jwks_expires_at = 0.0
_jwks_lock = asyncio.Lock()


async def _load_jwks(force_refresh: bool = False) -> dict[str, Any]:
    global _jwks, _jwks_expires_at

    if not force_refresh and _jwks is not None and time.monotonic() < _jwks_expires_at:
        return _jwks

    async with _jwks_lock:
        if not force_refresh and _jwks is not None and time.monotonic() < _jwks_expires_at:
            return _jwks

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(IAM_JWKS_URL)
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ServiceError(
                status_code=503,
                error_code="IAM_UNAVAILABLE",
                message="Identity provider is unavailable",
                details={"reason": str(exc)},
            ) from exc

        _jwks = payload
        _jwks_expires_at = time.monotonic() + JWKS_TTL_SECONDS
        return payload


def _find_signing_key(jwks: dict[str, Any], kid: str) -> Any | None:
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return jwt.PyJWK.from_dict(key).key
    return None


async def require_authenticated_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ServiceError(
            error_code="AUTH_REQUIRED",
            message="A valid bearer token is required",
            status_code=401,
        )

    token = credentials.credentials
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise jwt.InvalidTokenError("Token has no key id")

        jwks = await _load_jwks()
        signing_key = _find_signing_key(jwks, kid)
        if signing_key is None:
            jwks = await _load_jwks(force_refresh=True)
            signing_key = _find_signing_key(jwks, kid)
        if signing_key is None:
            raise jwt.InvalidTokenError("Signing key was not found")

        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=IAM_ISSUER,
            options={"verify_aud": False},
        )
        token_client = claims.get("azp") or claims.get("client_id")
        if token_client != IAM_CLIENT_ID:
            raise jwt.InvalidTokenError("Token was issued for a different client")
        return claims
    except jwt.PyJWTError as exc:
        raise ServiceError(
            status_code=401,
            error_code="INVALID_TOKEN",
            message="Bearer token validation failed",
            details={"reason": str(exc)},
        ) from exc
