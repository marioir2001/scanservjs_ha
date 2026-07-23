"""HTTP client for ScanservJS."""

from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import quote

from aiohttp import ClientError, ClientSession, ClientTimeout

from .const import DEFAULT_TIMEOUT


class ScanservJSApiError(Exception):
    """Raised when communication with ScanservJS fails."""


class ScanservJSClient:
    """Small asynchronous ScanservJS API client."""

    def __init__(
        self,
        session: ClientSession,
        base_url: str,
        verify_ssl: bool = True,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._verify_ssl = verify_ssl
        self._timeout = ClientTimeout(total=timeout)

    async def async_get_context(self) -> dict[str, Any]:
        """Return ScanservJS context data."""
        data = await self._request("GET", "/api/v1/context")
        if not isinstance(data, dict):
            raise ScanservJSApiError("Invalid response from /api/v1/context")
        return data

    async def async_scan(
        self,
        device_id: str,
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        """Start a scan using a saved integration profile."""
        params = dict(profile.get("params") or {})
        params.setdefault("deviceId", device_id)

        # Backwards compatibility with beta 0.3 profile fields.
        aliases = {
            "resolution": "resolution",
            "mode": "mode",
            "source": "source",
            "width": "width",
            "height": "height",
            "left": "left",
            "top": "top",
            "brightness": "brightness",
            "contrast": "contrast",
        }
        for profile_key, param_key in aliases.items():
            if profile_key in profile and param_key not in params:
                params[param_key] = profile[profile_key]

        source = str(params.get("source", profile.get("source", ""))).upper()
        pipeline = profile.get("pipeline") or profile.get("format")

        # Beta 0.3.1: ScanservJS expects the batch mode as a top-level field.
        # Existing ADF + PDF document profiles automatically get batch=auto.
        batch = profile.get("batch") or profile.get("batch_mode")
        if batch is None:
            is_pdf = isinstance(pipeline, str) and "PDF" in pipeline.upper()
            batch = "auto" if source == "ADF" and is_pdf else "none"

        payload: dict[str, Any] = {
            "version": str(profile.get("version", "3.1.0")),
            "batch": batch,
            "filters": list(profile.get("filters") or []),
            "index": int(profile.get("index", 1)),
            "params": params,
        }
        if pipeline:
            payload["pipeline"] = pipeline

        data = await self._request("POST", "/api/v1/scan", json=payload)
        return data if isinstance(data, dict) else {"result": data}

    async def async_rename_file(
        self,
        filename: str,
        new_filename: str,
    ) -> dict[str, Any]:
        """Rename a file in the ScanservJS output directory."""
        encoded_filename = quote(filename, safe="")

        data = await self._request(
            "PUT",
            f"/api/v1/files/{encoded_filename}",
            json={"newName": new_filename},
        )

        return data if isinstance(data, dict) else {"result": data}

    async def async_run_file_action(
        self, filename: str, action_name: str
    ) -> dict[str, Any]:
        """Run a configured ScanservJS action on a file."""
        encoded_filename = quote(filename, safe="")
        encoded_action = quote(action_name, safe="")
        data = await self._request(
            "POST",
            f"/api/v1/files/{encoded_filename}/actions/{encoded_action}",
        )
        return data if isinstance(data, dict) else {"result": data}

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self._base_url}{path}"
        try:
            async with self._session.request(
                method,
                url,
                ssl=self._verify_ssl,
                timeout=self._timeout,
                **kwargs,
            ) as response:
                text = await response.text()
                if response.status >= 400:
                    # Keep logs useful; do not dump complete proxy HTML pages.
                    compact = " ".join(text.split())[:500]
                    raise ScanservJSApiError(f"HTTP {response.status}: {compact}")
                if not text:
                    return {}
                try:
                    return await response.json(content_type=None)
                except (ValueError, TypeError):
                    return {"text": text}
        except asyncio.TimeoutError as err:
            raise ScanservJSApiError(
                f"Timeout while requesting {url}"
            ) from err
        except ClientError as err:
            raise ScanservJSApiError(f"Verbindungsfehler zu {url}: {err}") from err
