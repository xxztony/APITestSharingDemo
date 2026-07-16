from __future__ import annotations

import logging
import threading
import time
from typing import Any

import requests


class KeycloakTokenManager:
    """Caches Keycloak tokens and refreshes them before the access token expires."""

    def __init__(
        self,
        token_url: str,
        client_id: str,
        username: str,
        password: str,
        *,
        refresh_skew_seconds: int = 30,
        timeout_seconds: float = 10,
        session: requests.Session | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.token_url = token_url
        self.client_id = client_id
        self.username = username
        self.password = password
        self.refresh_skew_seconds = refresh_skew_seconds
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()
        self.logger = logger or logging.getLogger(__name__)

        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._access_expires_at = 0.0
        self._refresh_expires_at = 0.0
        self._lock = threading.RLock()
        self.refresh_count = 0

    def get_access_token(self) -> str:
        with self._lock:
            if self._access_token is None:
                self._password_grant()
            elif time.monotonic() >= self._access_expires_at - self.refresh_skew_seconds:
                self._refresh_or_reauthenticate()
            assert self._access_token is not None
            return self._access_token

    def refresh_access_token(self) -> str:
        with self._lock:
            if self._refresh_token is None:
                self._password_grant()
            else:
                self._refresh_or_reauthenticate()
            assert self._access_token is not None
            return self._access_token

    def invalidate_access_token(self) -> None:
        with self._lock:
            self._access_expires_at = 0.0

    def _password_grant(self) -> None:
        self._apply_token_response(
            self._request_token(
                {
                    "grant_type": "password",
                    "client_id": self.client_id,
                    "username": self.username,
                    "password": self.password,
                }
            ),
            grant_type="password",
        )

    def _refresh_or_reauthenticate(self) -> None:
        if self._refresh_token is None or time.monotonic() >= self._refresh_expires_at:
            self.logger.info("IAM refresh token unavailable or expired; authenticating again")
            self._password_grant()
            return

        try:
            payload = self._request_token(
                {
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "refresh_token": self._refresh_token,
                }
            )
        except requests.HTTPError as exc:
            self.logger.warning("IAM refresh failed with HTTP %s; authenticating again", exc.response.status_code)
            self._password_grant()
            return

        self.refresh_count += 1
        self._apply_token_response(payload, grant_type="refresh_token")

    def _request_token(self, form: dict[str, str]) -> dict[str, Any]:
        response = self.session.post(self.token_url, data=form, timeout=self.timeout_seconds)
        response.raise_for_status()
        payload = response.json()
        if "access_token" not in payload:
            raise RuntimeError("Keycloak token response has no access_token")
        return payload

    def _apply_token_response(self, payload: dict[str, Any], *, grant_type: str) -> None:
        now = time.monotonic()
        self._access_token = str(payload["access_token"])
        self._refresh_token = payload.get("refresh_token")
        self._access_expires_at = now + int(payload.get("expires_in", 0))
        self._refresh_expires_at = now + int(payload.get("refresh_expires_in", 0))
        self.logger.info(
            "IAM token received: grant=%s access_expires_in=%ss refresh_expires_in=%ss",
            grant_type,
            payload.get("expires_in"),
            payload.get("refresh_expires_in"),
        )
