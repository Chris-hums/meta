"""Thin wrapper around the Meta Graph API (Marketing API endpoints)."""
from __future__ import annotations

import time
from typing import Any, Optional

import requests

GRAPH_BASE = "https://graph.facebook.com"

# Errors worth a short backoff + retry (rate limiting / transient).
RETRYABLE_CODES = {4, 17, 32, 613}


class GraphAPIError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: Optional[int] = None,
        error_subcode: Optional[int] = None,
        error_type: Optional[str] = None,
        fbtrace_id: Optional[str] = None,
        http_status: Optional[int] = None,
        user_title: Optional[str] = None,
        user_msg: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.error_subcode = error_subcode
        self.error_type = error_type
        self.fbtrace_id = fbtrace_id
        self.http_status = http_status
        self.user_title = user_title
        self.user_msg = user_msg

    def __str__(self) -> str:
        bits = [super().__str__()]
        if self.code is not None:
            bits.append(f"code={self.code}")
        if self.error_subcode is not None:
            bits.append(f"subcode={self.error_subcode}")
        if self.fbtrace_id:
            bits.append(f"fbtrace_id={self.fbtrace_id}")
        return " | ".join(bits)


class GraphClient:
    def __init__(
        self,
        access_token: str,
        api_version: str = "v21.0",
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        self.access_token = access_token
        self.api_version = api_version
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

    def _url(self, path: str) -> str:
        if path.startswith("http"):
            return path
        return f"{GRAPH_BASE}/{self.api_version}/{path.lstrip('/')}"

    def _handle(self, resp: requests.Response) -> dict:
        try:
            data = resp.json()
        except ValueError:
            resp.raise_for_status()
            return {}
        if isinstance(data, dict) and "error" in data:
            err = data["error"] or {}
            raise GraphAPIError(
                err.get("message", "Unknown Graph API error"),
                code=err.get("code"),
                error_subcode=err.get("error_subcode"),
                error_type=err.get("type"),
                fbtrace_id=err.get("fbtrace_id"),
                http_status=resp.status_code,
                user_title=err.get("error_user_title"),
                user_msg=err.get("error_user_msg"),
            )
        if not resp.ok:
            resp.raise_for_status()
        return data

    def _request(self, method: str, url: str, **kwargs) -> dict:
        attempt = 0
        while True:
            attempt += 1
            resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
            try:
                return self._handle(resp)
            except GraphAPIError as exc:
                if exc.code in RETRYABLE_CODES and attempt <= self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise

    def get(self, path: str, params: Optional[dict] = None) -> dict:
        params = dict(params or {})
        params["access_token"] = self.access_token
        return self._request("GET", self._url(path), params=params)

    def get_all(
        self, path: str, params: Optional[dict] = None, limit: Optional[int] = None
    ) -> list[dict[str, Any]]:
        params = dict(params or {})
        params.setdefault("limit", 100)
        data = self.get(path, params)
        items = list(data.get("data", []))
        next_url = data.get("paging", {}).get("next")
        while next_url and (limit is None or len(items) < limit):
            data = self._request("GET", next_url)
            items.extend(data.get("data", []))
            next_url = data.get("paging", {}).get("next")
        return items[:limit] if limit else items

    def post(self, path: str, data: Optional[dict] = None) -> dict:
        payload = dict(data or {})
        payload["access_token"] = self.access_token
        return self._request("POST", self._url(path), data=payload)

    def delete(self, path: str, params: Optional[dict] = None) -> dict:
        params = dict(params or {})
        params["access_token"] = self.access_token
        return self._request("DELETE", self._url(path), params=params)
