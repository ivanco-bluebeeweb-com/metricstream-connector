"""Thin MetricStream REST client.

Auth model: static Bearer API Key. Base URL is user-supplied since
MetricStream is a per-tenant hosted instance (no shared default host).
"""
from __future__ import annotations

from typing import Any

import httpx


class MetricStreamError(RuntimeError):
    """A safe provider-facing error; never includes credentials."""

    def __init__(self, message: str, retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


class MetricStreamClient:
    """REST client for the MetricStream API, scoped to one tenant."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        *,
        timeout: float = 30.0,
    ):
        if not api_key:
            raise MetricStreamError("API Key is required.")
        if not base_url:
            raise MetricStreamError("Base URL is required (e.g. https://your-instance.metricstream.com).")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        if not self.base_url.startswith("http"):
            self.base_url = f"https://{self.base_url}"
        self.timeout = timeout

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> tuple[Any, httpx.Response]:
        url = f"{self.base_url}{path}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.request(
                    method, url, params=params, json=json_body, headers=headers,
                )
            except httpx.TimeoutException:
                raise MetricStreamError("MetricStream API request timed out.", retryable=True)
            except httpx.ConnectError:
                raise MetricStreamError("Could not reach the MetricStream instance. Check the instance URL.", retryable=True)

        if resp.status_code == 401:
            raise MetricStreamError("Authentication failed. The API Key may be invalid or expired.")
        if resp.status_code == 403:
            raise MetricStreamError("Access denied. The API Key may lack permission for this operation.")
        if resp.status_code == 404:
            raise MetricStreamError("Not found. Check the id and try again.")
        if resp.status_code == 429:
            raise MetricStreamError("Rate limited by MetricStream. Try again shortly.", retryable=True)
        if resp.status_code >= 500:
            raise MetricStreamError("MetricStream is currently unavailable.", retryable=True)
        if resp.status_code >= 400:
            raise MetricStreamError(f"MetricStream API error ({resp.status_code}).")

        try:
            data = resp.json() if resp.content else {}
        except ValueError:
            data = {}
        return data, resp
