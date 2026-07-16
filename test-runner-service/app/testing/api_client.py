from __future__ import annotations

import json
import logging
from typing import Any
from urllib.parse import urljoin

import requests

from app.testing.token_manager import KeycloakTokenManager


SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "proxy-authorization"}


def _redact_headers(headers: dict[str, Any]) -> dict[str, Any]:
    return {
        key: "<redacted>" if key.lower() in SENSITIVE_HEADERS else value
        for key, value in headers.items()
    }


def _response_body(response: requests.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text[:100_000]


def _log_json_attachment(logger: logging.Logger, message: str, name: str, payload: dict[str, Any]) -> None:
    rendered = json.dumps(payload, ensure_ascii=True, indent=2, default=str)
    try:
        logger.info(
            message,
            attachment={"name": name, "data": rendered.encode("utf-8"), "mime": "application/json"},
        )
    except TypeError:
        logger.info("%s\n%s", message, rendered)


class IamApiClient:
    """A requests-based API client with bearer auth, refresh, retry, and RP logs."""

    def __init__(
        self,
        base_url: str,
        token_manager: KeycloakTokenManager,
        *,
        session: requests.Session | None = None,
        logger: logging.Logger | None = None,
        timeout_seconds: float = 10,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.token_manager = token_manager
        self.session = session or requests.Session()
        self.logger = logger or logging.getLogger(__name__)
        self.timeout_seconds = timeout_seconds

    def request(
        self,
        method: str,
        path: str,
        *,
        authenticate: bool = True,
        retry_on_unauthorized: bool = True,
        **kwargs: Any,
    ) -> requests.Response:
        url = urljoin(self.base_url, path.lstrip("/"))
        headers = dict(kwargs.pop("headers", {}))
        if authenticate:
            headers["Authorization"] = f"Bearer {self.token_manager.get_access_token()}"

        request_log = {
            "method": method.upper(),
            "url": url,
            "headers": _redact_headers(headers),
            "query": kwargs.get("params"),
            "json": kwargs.get("json"),
            "body": kwargs.get("data"),
        }
        _log_json_attachment(self.logger, f"HTTP request: {method.upper()} {url}", "request.json", request_log)

        response = self.session.request(
            method,
            url,
            headers=headers,
            timeout=kwargs.pop("timeout", self.timeout_seconds),
            **kwargs,
        )

        if authenticate and retry_on_unauthorized and response.status_code == 401:
            self.logger.warning("BFF returned 401; refreshing the IAM token and retrying once")
            headers["Authorization"] = f"Bearer {self.token_manager.refresh_access_token()}"
            response = self.session.request(
                method,
                url,
                headers=headers,
                timeout=self.timeout_seconds,
                **kwargs,
            )

        response_log = {
            "status": response.status_code,
            "elapsedMs": round(response.elapsed.total_seconds() * 1000, 2),
            "headers": _redact_headers(dict(response.headers)),
            "body": _response_body(response),
        }
        _log_json_attachment(
            self.logger,
            f"HTTP response: {response.status_code} {method.upper()} {url}",
            "response.json",
            response_log,
        )
        return response

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", path, **kwargs)
