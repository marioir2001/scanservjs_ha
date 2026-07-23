"""Button entities for ScanservJS profiles."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory

from .api import ScanservJSApiError
from .const import CONF_PROFILES, DOMAIN
from .runtime import ScanservJSRuntime

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities) -> None:
    runtime: ScanservJSRuntime = entry.runtime_data
    profiles = entry.options.get(CONF_PROFILES, entry.data.get(CONF_PROFILES, []))
    if isinstance(profiles, dict):
        profiles = [dict(value, name=key) for key, value in profiles.items()]
    async_add_entities(
        ScanservJSProfileButton(entry, runtime, profile, index)
        for index, profile in enumerate(profiles or [])
    )


class ScanservJSProfileButton(ButtonEntity):
    """Starts a ScanservJS profile."""

    _attr_has_entity_name = True

    def __init__(self, entry, runtime: ScanservJSRuntime, profile: dict[str, Any], index: int) -> None:
        self._entry = entry
        self._runtime = runtime
        self._profile = profile
        self._name = str(profile.get("name") or profile.get("title") or f"Profile {index + 1}")
        profile_id = profile.get("id") or profile.get("slug") or index
        self._attr_unique_id = f"{entry.entry_id}_profile_{profile_id}"
        self._attr_name = self._name
        self._attr_icon = _profile_icon(profile)
        self._remove_listener = None

    async def async_added_to_hass(self) -> None:
        """Subscribe to shared runtime updates."""
        self._remove_listener = self._runtime.add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe from shared runtime updates."""
        if self._remove_listener:
            self._remove_listener()
            self._remove_listener = None

    @property
    def available(self) -> bool:
        """Disable all scan buttons while a scan is running."""
        return self._runtime.status != "scanning"

    @property
    def device_info(self) -> DeviceInfo:
        device = self._runtime.device
        name = device.get("name") or device.get("id") or "ScanservJS"
        model = name.split(":")[-1].strip()
        manufacturer = "Brother" if "Brother" in model else "ScanservJS"
        return DeviceInfo(
            identifiers={(DOMAIN, str(device.get("id", self._entry.entry_id)))},
            name=model,
            manufacturer=manufacturer,
            model=model.replace("Brother ", "") if manufacturer == "Brother" else model,
            configuration_url=self._entry.data.get("url"),
        )

    async def async_press(self) -> None:
        device_id = str(self._runtime.device.get("id") or self._entry.data.get("device_id"))
        try:
            await self._runtime.async_scan(device_id, self._profile)
        except ScanservJSApiError:
            _LOGGER.exception("Scan profile '%s' failed", self._name)
            raise


def _profile_icon(profile: dict[str, Any]) -> str:
    """Return an icon based on the actual output format and scan mode."""
    pipeline = str(profile.get("pipeline", "")).strip().upper()
    params = profile.get("params") if isinstance(profile.get("params"), dict) else {}
    mode = str(profile.get("mode") or params.get("mode") or "").lower()

    # A PDF pipeline can contain JPG internally; it is still a document output.
    if pipeline.startswith("PDF") or "| PDF" in pipeline:
        if mode in {"gray", "grey", "lineart", "black & white", "black-and-white"}:
            return "mdi:text-box-outline"
        return "mdi:file-document"

    if pipeline.startswith(("JPG", "JPEG", "PNG", "TIF", "TIFF")):
        return "mdi:image-outline"

    return "mdi:scanner"
