"""ScanservJS integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ScanservJSClient
from .const import CONF_PROFILES, CONF_URL, CONF_VERIFY_SSL, DOMAIN, PLATFORMS
from .runtime import ScanservJSRuntime


type ScanservJSConfigEntry = ConfigEntry[ScanservJSRuntime]


async def async_setup_entry(hass: HomeAssistant, entry: ScanservJSConfigEntry) -> bool:
    # Remove only the exact three profiles that beta 0.3.1 accidentally seeded.
    # User-created profiles live in entry.options and are never touched.
    seeded = entry.data.get(CONF_PROFILES)
    seeded_ids = {p.get("id") for p in seeded} if isinstance(seeded, list) else set()
    if CONF_PROFILES not in entry.options and seeded_ids == {"document_bw", "document_color", "photo"}:
        data = dict(entry.data)
        data.pop(CONF_PROFILES, None)
        hass.config_entries.async_update_entry(entry, data=data, options={CONF_PROFILES: []})
    session = async_get_clientsession(hass, verify_ssl=entry.data.get(CONF_VERIFY_SSL, True))
    client = ScanservJSClient(
        session,
        entry.data[CONF_URL],
        verify_ssl=entry.data.get(CONF_VERIFY_SSL, True),
    )
    context = await client.async_get_context()
    devices = context.get("devices") or []
    selected_id = entry.data.get("device_id")
    device = next((item for item in devices if item.get("id") == selected_id), None)
    if device is None:
        device = devices[0] if devices else {"id": selected_id or "scanservjs", "name": "ScanservJS"}

    entry.runtime_data = ScanservJSRuntime(client, device)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ScanservJSConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload_entry(hass: HomeAssistant, entry: ScanservJSConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
