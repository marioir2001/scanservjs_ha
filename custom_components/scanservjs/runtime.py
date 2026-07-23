"""Runtime state for ScanservJS."""

from __future__ import annotations

import asyncio
from datetime import datetime
import re
from pathlib import PurePath
from typing import Any, Callable

from homeassistant.util import dt as dt_util

from .api import ScanservJSApiError, ScanservJSClient
from .const import STATUS_ERROR, STATUS_IDLE, STATUS_SCANNING, STATUS_SUCCESS


_INVALID_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|\x00-\x1f]+')


class ScanservJSRuntime:
    """Holds API client and shared entity state."""

    def __init__(self, client: ScanservJSClient, device: dict[str, Any]) -> None:
        self.client = client
        self.device = device
        self.status = STATUS_IDLE
        self.last_scan: datetime | None = None
        self.last_file: str | None = None
        self.last_file_info: dict[str, Any] = {}
        self.last_error: str | None = None
        self._listeners: set[Callable[[], None]] = set()
        self._scan_lock = asyncio.Lock()

    def add_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        self._listeners.add(listener)

        def remove() -> None:
            self._listeners.discard(listener)

        return remove

    def _notify(self) -> None:
        for listener in tuple(self._listeners):
            listener()

    async def async_scan(self, device_id: str, profile: dict[str, Any]) -> dict[str, Any]:
        """Run a scan, optionally rename its output, then run a file action."""
        async with self._scan_lock:
            self.status = STATUS_SCANNING
            self.last_error = None
            self._notify()
            try:
                result = await self.client.async_scan(device_id, profile)
                filename, file_info = _extract_file(result)
                if not filename:
                    raise ScanservJSApiError(
                        "ScanservJS hat keinen Dateinamen zurückgegeben."
                    )

                prefix = str(profile.get("filename_prefix") or "").strip()
                if prefix:
                    new_filename = _build_filename(prefix, filename)
                    rename_result = await self.client.async_rename_file(
                        filename, new_filename
                    )
                    returned_filename, returned_file_info = _extract_file(
                        rename_result
                    )
                    filename = returned_filename or new_filename
                    file_info = _renamed_file_info(file_info, filename)
                    file_info.update(returned_file_info)

                action = str(profile.get("file_action") or "").strip()
                if action:
                    await self.client.async_run_file_action(filename, action)
                    file_info["action"] = action

            except Exception as err:
                self.status = STATUS_ERROR
                self.last_error = str(err)
                self._notify()
                raise

            self.status = STATUS_SUCCESS
            self.last_scan = dt_util.utcnow()
            self.last_file = filename
            self.last_file_info = file_info
            self._notify()
            return result


def _build_filename(prefix: str, original_filename: str) -> str:
    """Build a safe filename from a profile prefix, timestamp and old extension."""
    clean_prefix = _INVALID_FILENAME_CHARS.sub("_", prefix).strip(" ._-")
    if not clean_prefix:
        clean_prefix = "scan"
    extension = PurePath(original_filename).suffix.lower()
    timestamp = dt_util.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{clean_prefix}_{timestamp}{extension}"


def _renamed_file_info(file_info: dict[str, Any], new_filename: str) -> dict[str, Any]:
    """Return metadata adjusted to the renamed output file."""
    updated = dict(file_info)
    updated["extension"] = PurePath(new_filename).suffix.lower()
    fullname = updated.get("fullname")
    if isinstance(fullname, str) and fullname:
        updated["fullname"] = str(PurePath(fullname).with_name(new_filename))
    return updated


def _extract_file(result: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    """Extract the output filename and metadata from a ScanservJS response."""
    file_data = result.get("file")
    if isinstance(file_data, dict):
        name = file_data.get("name")
        if not isinstance(name, str) or not name:
            fullname = file_data.get("fullname")
            name = PurePath(fullname).name if isinstance(fullname, str) and fullname else None

        attributes = {
            key: value
            for key, value in {
                "fullname": file_data.get("fullname"),
                "extension": file_data.get("extension"),
                "last_modified": file_data.get("lastModified"),
                "size": file_data.get("size"),
                "size_string": file_data.get("sizeString"),
                "is_directory": file_data.get("isDirectory"),
                "path": file_data.get("path"),
            }.items()
            if value is not None
        }
        return name, attributes

    # Some endpoints, including file rename, may return FileInfo directly
    # instead of wrapping it inside a ``file`` object.
    direct_name = result.get("name")
    if isinstance(direct_name, str) and direct_name:
        attributes = {
            key: value
            for key, value in {
                "fullname": result.get("fullname"),
                "extension": result.get("extension"),
                "last_modified": result.get("lastModified"),
                "size": result.get("size"),
                "size_string": result.get("sizeString"),
                "is_directory": result.get("isDirectory"),
                "path": result.get("path"),
            }.items()
            if value is not None
        }
        return direct_name, attributes

    # Compatibility with other or older response shapes.
    for key in ("filename", "path", "output", "url"):
        value = result.get(key)
        if isinstance(value, str) and value:
            return PurePath(value).name, {}
    for key in ("files", "outputs"):
        value = result.get(key)
        if isinstance(value, list) and value:
            first = value[0]
            if isinstance(first, str):
                return PurePath(first).name, {}
            if isinstance(first, dict):
                return _extract_file(first)
    return None, {}
