"""Thin client for the Pinlyx public REST API (https://api.pinlyx.com/v1).

Auth: the key is sent as `X-Api-Key`; the API also accepts `Authorization: Bearer csk_live_...`.
The host is fixed on purpose: the key is only ever sent to api.pinlyx.com.
"""

from __future__ import annotations

from typing import Any

import requests

BASE_URL = "https://api.pinlyx.com"
TIMEOUT_SECONDS = 30


class PinlyxApiError(Exception):
    """A non-2xx answer from the Pinlyx API (shape: {error, message, details})."""

    def __init__(self, status: int, code: str, message: str, details: Any = None):
        self.status = status
        self.code = code
        self.details = details
        super().__init__(f"Pinlyx API error {status} ({code}): {message}")


class PinlyxClient:
    def __init__(self, credentials: dict[str, Any], session: requests.Session | None = None):
        api_key = (credentials.get("api_key") or "").strip()
        if not api_key:
            raise ValueError("Pinlyx API key is not configured.")
        self._headers = {"X-Api-Key": api_key, "Accept": "application/json"}
        workspace_id = str(credentials.get("workspace_id") or "").strip()
        if workspace_id:
            self._headers["X-Workspace-Id"] = workspace_id
        self._session = session or requests.Session()

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        response = self._session.request(
            method,
            f"{BASE_URL}{path}",
            headers=self._headers,
            params=params,
            json=json_body,
            timeout=TIMEOUT_SECONDS,
        )
        if response.status_code >= 400:
            code, message, details = "error", response.text[:300], None
            try:
                body = response.json()
                if isinstance(body, dict):
                    code = str(body.get("error") or code)
                    message = str(body.get("message") or message)
                    details = body.get("details")
            except ValueError:
                pass
            raise PinlyxApiError(response.status_code, code, message, details)
        if not response.content:
            return None
        return response.json()

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self.request("GET", path, params=params)

    def post(self, path: str, json_body: dict[str, Any]) -> Any:
        return self.request("POST", path, json_body=json_body)
