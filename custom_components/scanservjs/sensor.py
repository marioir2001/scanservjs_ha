"""Sensors for ScanservJS."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .runtime import ScanservJSRuntime


async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities) -> None:
    runtime: ScanservJSRuntime = entry.runtime_data
    async_add_entities([
        ScanservJSStatusSensor(entry, runtime),
        ScanservJSLastScanSensor(entry, runtime),
        ScanservJSLastFileSensor(entry, runtime),
    ])


class _BaseSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, entry, runtime: ScanservJSRuntime) -> None:
        self._entry = entry
        self._runtime = runtime
        self._remove_listener = None

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

    async def async_added_to_hass(self) -> None:
        self._remove_listener = self._runtime.add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        if self._remove_listener:
            self._remove_listener()


class ScanservJSStatusSensor(_BaseSensor):
    _attr_translation_key = "status"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["idle", "scanning", "success", "error"]
    _attr_icon = "mdi:scanner"

    def __init__(self, entry, runtime) -> None:
        super().__init__(entry, runtime)
        self._attr_unique_id = f"{entry.entry_id}_status"

    @property
    def native_value(self):
        return self._runtime.status

    @property
    def extra_state_attributes(self):
        return {"last_error": self._runtime.last_error} if self._runtime.last_error else {}


class ScanservJSLastScanSensor(_BaseSensor):
    _attr_translation_key = "last_scan"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, entry, runtime) -> None:
        super().__init__(entry, runtime)
        self._attr_unique_id = f"{entry.entry_id}_last_scan"

    @property
    def native_value(self):
        return self._runtime.last_scan


class ScanservJSLastFileSensor(_BaseSensor):
    _attr_translation_key = "last_file"
    _attr_icon = "mdi:file-check-outline"

    def __init__(self, entry, runtime) -> None:
        super().__init__(entry, runtime)
        self._attr_unique_id = f"{entry.entry_id}_last_file"

    @property
    def native_value(self):
        return self._runtime.last_file

    @property
    def extra_state_attributes(self):
        return self._runtime.last_file_info or None

    @property
    def icon(self) -> str:
        extension = str(self._runtime.last_file_info.get("extension", "")).lower()
        if extension == ".pdf":
            return "mdi:file-pdf-box"
        if extension in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".tif", ".tiff"}:
            return "mdi:file-image-outline"
        return "mdi:file-check-outline"
