"""Config and options flows for ScanservJS."""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ScanservJSApiError, ScanservJSClient
from .const import CONF_PROFILES, CONF_URL, CONF_VERIFY_SSL, DOMAIN


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip().lower()).strip("_")
    return slug or "profile"


def _feature_options(device: dict[str, Any], key: str, fallback: list[Any]) -> list[Any]:
    values = device.get("features", {}).get(key, {}).get("options")
    return values if isinstance(values, list) and values else fallback


def _pick(values: list[Any], preferred: Any, fallback: Any = None) -> Any:
    if preferred in values:
        return preferred
    return values[0] if values else fallback


def _paper_sizes(context: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for item in context.get("paperSizes", []):
        dims = item.get("dimensions", {})
        if "x" in dims and "y" in dims:
            result.append({"name": item.get("name", "Paper size"), "width": dims["x"], "height": dims["y"]})
    return result or [{"name": "A4", "width": 210, "height": 297}]


class ScanservJSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                client = ScanservJSClient(
                    async_get_clientsession(self.hass, verify_ssl=user_input[CONF_VERIFY_SSL]),
                    user_input[CONF_URL],
                    user_input[CONF_VERIFY_SSL],
                )
                context = await client.async_get_context()
                devices = context.get("devices") or []
                device = devices[0] if devices else {}
                if not device:
                    errors["base"] = "no_devices"
                else:
                    await self.async_set_unique_id(str(device.get("id") or user_input[CONF_URL]))
                    self._abort_if_unique_id_configured()
                    data = dict(user_input)
                    data["device_id"] = device.get("id")
                    # Profiles are deliberately user-defined. Do not seed defaults.
                    return self.async_create_entry(
                        title=user_input[CONF_NAME],
                        data=data,
                        options={CONF_PROFILES: []},
                    )
            except ScanservJSApiError:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME, default="ScanservJS"): str,
                vol.Required(CONF_URL, default="http://192.168.1.10:8080"): str,
                vol.Required(CONF_VERIFY_SSL, default=True): bool,
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> OptionsFlow:
        return ScanservJSOptionsFlow()


class ScanservJSOptionsFlow(OptionsFlow):
    """Create and manage user-defined scan profiles."""

    def __init__(self) -> None:
        self._editing_id: str | None = None
        self._template_defaults: dict[str, Any] | None = None
        self._context: dict[str, Any] = {}
        self._device: dict[str, Any] = {}

    @property
    def _profiles(self) -> list[dict[str, Any]]:
        return deepcopy(list(self.config_entry.options.get(CONF_PROFILES, [])))

    async def _load_context(self) -> None:
        if self._context:
            return
        client = ScanservJSClient(
            async_get_clientsession(self.hass, verify_ssl=self.config_entry.data.get(CONF_VERIFY_SSL, True)),
            self.config_entry.data[CONF_URL],
            self.config_entry.data.get(CONF_VERIFY_SSL, True),
        )
        self._context = await client.async_get_context()
        devices = self._context.get("devices") or []
        selected = self.config_entry.data.get("device_id")
        self._device = next((d for d in devices if d.get("id") == selected), devices[0] if devices else {})

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        try:
            await self._load_context()
        except ScanservJSApiError:
            return self.async_abort(reason="cannot_connect")
        profiles = self._profiles
        options = ["add_profile"]
        if profiles:
            options.extend(["edit_profile", "move_profile", "delete_profile"])
        return self.async_show_menu(step_id="init", menu_options=options)

    async def async_step_add_profile(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._template_defaults = self._defaults_for_template(user_input["template"])
            return await self.async_step_add_profile_data()
        return self.async_show_form(
            step_id="add_profile",
            data_schema=vol.Schema({
                vol.Required("template", default="document_gray"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=["document_gray", "document_color", "photo", "custom"],
                        translation_key="profile_template",
                    )
                )
            }),
        )

    async def async_step_add_profile_data(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return await self._profile_form("add_profile_data", user_input, self._template_defaults)

    def _defaults_for_template(self, template: str) -> dict[str, Any]:
        sources = _feature_options(self._device, "--source", ["Flatbed"])
        modes = _feature_options(self._device, "--mode", ["Color"])
        resolutions = _feature_options(self._device, "--resolution", [300])
        settings = self._device.get("settings", {})
        pipelines = settings.get("pipeline", {}).get("options", [])
        filters = settings.get("filters", {}).get("options", [])
        pdf = _pick(pipelines, "PDF (JPG | @:pipeline.high-quality)", "PDF (JPG | @:pipeline.high-quality)")
        jpg = _pick(pipelines, "JPG | @:pipeline.high-quality", "JPG | @:pipeline.high-quality")
        if template == "document_gray":
            return {"name": "Dokument S/W", "source": _pick(sources, "ADF", "Flatbed"), "resolution": _pick(resolutions, 300, 300), "mode": _pick(modes, "Gray", "Color"), "pipeline": pdf, "filters": ["filter.auto-level"] if "filter.auto-level" in filters else [], "batch": "auto"}
        if template == "document_color":
            return {"name": "Dokument Farbe", "source": _pick(sources, "ADF", "Flatbed"), "resolution": _pick(resolutions, 300, 300), "mode": _pick(modes, "Color", "Color"), "pipeline": pdf, "filters": ["filter.auto-level"] if "filter.auto-level" in filters else [], "batch": "auto"}
        if template == "photo":
            return {"name": "Foto", "source": _pick(sources, "Flatbed", "Flatbed"), "resolution": _pick(resolutions, 600, 300), "mode": _pick(modes, "Color", "Color"), "pipeline": jpg, "filters": [], "batch": "none"}
        return {"name": "", "source": sources[0], "resolution": resolutions[0], "mode": modes[0], "pipeline": pipelines[0] if pipelines else pdf, "filters": [], "batch": "none"}

    async def async_step_edit_profile(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        profiles = self._profiles
        if user_input is not None:
            self._editing_id = user_input["profile"]
            current = next(p for p in profiles if p["id"] == self._editing_id)
            return await self._profile_form("edit_profile_data", None, current)
        return self.async_show_form(step_id="edit_profile", data_schema=vol.Schema({
            vol.Required("profile"): selector.SelectSelector(selector.SelectSelectorConfig(options=[{"value": p["id"], "label": p["name"]} for p in profiles]))
        }))

    async def async_step_edit_profile_data(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        current = next(p for p in self._profiles if p["id"] == self._editing_id)
        return await self._profile_form("edit_profile_data", user_input, current)

    async def _profile_form(self, step_id: str, user_input: dict[str, Any] | None, current: dict[str, Any] | None) -> ConfigFlowResult:
        profiles = self._profiles
        errors: dict[str, str] = {}
        if user_input is not None:
            profile_id = _slug(user_input[CONF_NAME])
            if any(p["id"] == profile_id and p["id"] != self._editing_id for p in profiles):
                errors["base"] = "profile_exists"
            else:
                paper = next(p for p in _paper_sizes(self._context) if p["name"] == user_input["paper_size"])
                profile = {
                    "id": profile_id,
                    "name": user_input[CONF_NAME].strip(),
                    "version": "3.1.0",
                    "batch": user_input["batch"],
                    "filters": list(user_input.get("filters", [])),
                    "index": 1,
                    "pipeline": user_input["pipeline"],
                    "params": {
                        "deviceId": self._device.get("id"),
                        "resolution": int(user_input["resolution"]),
                        "width": paper["width"], "height": paper["height"],
                        "left": 0, "top": 0,
                        "mode": user_input["mode"], "source": user_input["source"],
                        "brightness": int(user_input["brightness"]),
                        "contrast": int(user_input["contrast"]),
                    },
                    # Flat aliases retained for readable attributes/backwards compatibility.
                    "resolution": int(user_input["resolution"]), "mode": user_input["mode"],
                    "source": user_input["source"], "width": paper["width"], "height": paper["height"],
                    "paper_size": paper["name"], "brightness": int(user_input["brightness"]),
                    "contrast": int(user_input["contrast"]),
                    "filename_prefix": str(user_input.get("filename_prefix", "")).strip(),
                    "file_action": str(user_input.get("file_action", "")).strip(),
                }
                if self._editing_id:
                    profiles = [profile if p["id"] == self._editing_id else p for p in profiles]
                else:
                    profiles.append(profile)
                return self.async_create_entry(title="", data={CONF_PROFILES: profiles})

        await self._load_context()
        defaults = current or {}
        params = defaults.get("params", {})
        sources = _feature_options(self._device, "--source", ["Flatbed"])
        modes = _feature_options(self._device, "--mode", ["Color"])
        resolutions = _feature_options(self._device, "--resolution", [300])
        settings = self._device.get("settings", {})
        pipelines = settings.get("pipeline", {}).get("options", []) or ["PDF (JPG | @:pipeline.high-quality)"]
        filters = settings.get("filters", {}).get("options", [])
        batch_options = settings.get("batchMode", {}).get("options", []) or ["none", "manual", "auto", "auto-collate-standard"]
        papers = _paper_sizes(self._context)
        context_actions = self._context.get("actions") or []
        actions = [action for action in context_actions if isinstance(action, str) and action]
        action_options = [{"value": "", "label": "—"}] + [
            {"value": action, "label": action} for action in actions
        ]
        selected_action = str(defaults.get("file_action", ""))
        if selected_action and selected_action not in actions:
            action_options.append({"value": selected_action, "label": selected_action})

        schema = vol.Schema({
            vol.Required(CONF_NAME, default=defaults.get("name", "")): selector.TextSelector(),
            vol.Required("source", default=defaults.get("source", params.get("source", sources[0]))): selector.SelectSelector(selector.SelectSelectorConfig(options=sources)),
            vol.Required("resolution", default=str(defaults.get("resolution", params.get("resolution", resolutions[0])))): selector.SelectSelector(selector.SelectSelectorConfig(options=[{"value": str(v), "label": f"{v} DPI"} for v in resolutions])),
            vol.Required("mode", default=defaults.get("mode", params.get("mode", modes[0]))): selector.SelectSelector(selector.SelectSelectorConfig(options=modes)),
            vol.Required("paper_size", default=defaults.get("paper_size", papers[0]["name"])): selector.SelectSelector(selector.SelectSelectorConfig(options=[{"value": p["name"], "label": p["name"]} for p in papers])),
            vol.Required("pipeline", default=defaults.get("pipeline", pipelines[0])): selector.SelectSelector(selector.SelectSelectorConfig(options=pipelines)),
            vol.Required("batch", default=defaults.get("batch", "none")): selector.SelectSelector(selector.SelectSelectorConfig(options=batch_options, translation_key="batch_mode")),
            vol.Optional("filters", default=defaults.get("filters", [])): selector.SelectSelector(selector.SelectSelectorConfig(options=filters, multiple=True)),
            vol.Required("brightness", default=defaults.get("brightness", params.get("brightness", 0))): selector.NumberSelector(selector.NumberSelectorConfig(min=-100, max=100, step=1, mode=selector.NumberSelectorMode.SLIDER)),
            vol.Required("contrast", default=defaults.get("contrast", params.get("contrast", 0))): selector.NumberSelector(selector.NumberSelectorConfig(min=-100, max=100, step=1, mode=selector.NumberSelectorMode.SLIDER)),
            vol.Optional(
                "filename_prefix",
                description={
                    "suggested_value": defaults.get("filename_prefix", "")
                },
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.TEXT
                )
            ),
            vol.Optional("file_action", default=selected_action): selector.SelectSelector(
                selector.SelectSelectorConfig(options=action_options)
            ),
        })
        return self.async_show_form(step_id=step_id, data_schema=schema, errors=errors)

    async def async_step_move_profile(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        profiles = self._profiles
        if user_input is not None:
            selected_id = user_input["profile"]
            new_position = int(user_input["position"]) - 1
            selected = next(p for p in profiles if p["id"] == selected_id)
            profiles = [p for p in profiles if p["id"] != selected_id]
            profiles.insert(max(0, min(new_position, len(profiles))), selected)
            return self.async_create_entry(title="", data={CONF_PROFILES: profiles})
        return self.async_show_form(step_id="move_profile", data_schema=vol.Schema({
            vol.Required("profile"): selector.SelectSelector(selector.SelectSelectorConfig(options=[{"value": p["id"], "label": p["name"]} for p in profiles])),
            vol.Required("position", default=1): selector.NumberSelector(selector.NumberSelectorConfig(min=1, max=len(profiles), step=1, mode=selector.NumberSelectorMode.BOX)),
        }))

    async def async_step_delete_profile(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        profiles = self._profiles
        if user_input is not None:
            return self.async_create_entry(title="", data={CONF_PROFILES: [p for p in profiles if p["id"] != user_input["profile"]]})
        return self.async_show_form(step_id="delete_profile", data_schema=vol.Schema({
            vol.Required("profile"): selector.SelectSelector(selector.SelectSelectorConfig(options=[{"value": p["id"], "label": p["name"]} for p in profiles]))
        }))
