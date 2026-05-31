"""Hybrid cloud/local MY HEAT API client and local state mapping."""

from __future__ import annotations

import asyncio
import copy
import logging
import time
from typing import TYPE_CHECKING, Any

from .const import (
    DEFAULT_CLOUD_POLL_INTERVAL,
    DEFAULT_LOCAL_POLL_INTERVAL,
    LOCAL_SENTINEL,
)
from .local_api import LocalApiError, LocalResponseError, LocalValidationError

if TYPE_CHECKING:
    from .api import MhApiClient
    from .local_api import LocalApiClient

_LOGGER = logging.getLogger(__package__)


def _is_sentinel(value: Any) -> bool:
    try:
        return float(value) <= -16777215
    except TypeError, ValueError:
        return False


def _clean_number(value: Any) -> float | None:
    if value is None or _is_sentinel(value):
        return None

    try:
        return float(value)
    except TypeError, ValueError:
        return None


def _clean_int(value: Any) -> int | None:
    number = _clean_number(value)
    if number is None:
        return None
    return int(number)


def _state_map(obj: dict[str, Any], key: str) -> dict[str, Any]:
    value = obj.get(key)
    return value if isinstance(value, dict) else {}


def _setting(obj: dict[str, Any], key: str) -> Any:
    return _state_map(obj, "s").get(key)


def _state(obj: dict[str, Any], key: str) -> Any:
    return _state_map(obj, "st").get(key)


def _is_nonzero(value: Any) -> bool:
    try:
        return int(float(value)) != 0
    except TypeError, ValueError:
        return False


def _severity_desc(severity: int | None) -> str:
    return {
        1: "Normal",
        32: "Warning",
        64: "Critical",
    }.get(severity, "Unknown")


def _env_type(obj: dict[str, Any], controlled: bool) -> str:
    explicit = _setting(obj, "p3028")
    if explicit:
        return str(explicit)

    obj_type = obj.get("t")
    if obj_type == 109:
        return "humidity"
    if obj_type == 113:
        return "pressure"
    if controlled:
        return "room_temperature"
    return "temperature"


def _eng_type(obj_type: Any) -> str:
    if obj_type in (305, 308, 309):
        return "valve"
    if obj_type == 302:
        return "engineering"
    return "engineering"


def _safe_device_state(device_state: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(device_state, dict):
        return {}

    sanitized = dict(device_state)
    sanitized.pop("regkey", None)
    return sanitized


def _map_env(obj: dict[str, Any]) -> dict[str, Any]:
    controlled = _is_nonzero(_setting(obj, "p3026"))
    severity = _clean_int(obj.get("sev"))
    target = _clean_number(_setting(obj, "p3008"))

    data: dict[str, Any] = {
        "id": obj.get("i"),
        "type": _env_type(obj, controlled),
        "name": obj.get("n", ""),
        "value": _clean_number(_state(obj, "p1")),
        "target": target,
        "demand": _is_nonzero(_state(obj, "p4")),
        "severity": severity,
        "severityDesc": _severity_desc(severity),
        "localControl": {
            "target": controlled,
            "curve": _is_nonzero(_setting(obj, "p3049")),
        },
        "local": {
            "typeCode": obj.get("t"),
            "flags": obj.get("f"),
            "state": _state_map(obj, "st"),
            "settings": _state_map(obj, "s"),
            "curveId": _clean_int(_setting(obj, "p3022")),
        },
    }

    min_temp = _clean_number(_setting(obj, "p3012"))
    max_temp = _clean_number(_setting(obj, "p3011"))
    if min_temp is not None:
        data["minTemp"] = min_temp
    if max_temp is not None:
        data["maxTemp"] = max_temp

    return data


def _map_heater(obj: dict[str, Any]) -> dict[str, Any]:
    severity = _clean_int(obj.get("sev"))
    return {
        "id": obj.get("i"),
        "name": obj.get("n", ""),
        "disabled": str(_setting(obj, "p3013")) == "1",
        "flowTemp": _clean_number(_state(obj, "p100")),
        "returnTemp": _clean_number(_state(obj, "p101")),
        "pressure": _clean_number(_state(obj, "p109")),
        "targetTemp": 0,
        "burnerHeating": False,
        "burnerWater": False,
        "modulation": None,
        "severity": severity,
        "severityDesc": _severity_desc(severity),
        "localControl": {
            "enabled": True,
        },
        "local": {
            "typeCode": obj.get("t"),
            "flags": obj.get("f"),
            "state": _state_map(obj, "st"),
            "settings": _state_map(obj, "s"),
        },
    }


def _map_eng(obj: dict[str, Any]) -> dict[str, Any]:
    severity = _clean_int(obj.get("sev"))
    mode = _clean_int(_setting(obj, "p3008"))
    state = _clean_int(_state(obj, "p4"))
    return {
        "id": obj.get("i"),
        "type": _eng_type(obj.get("t")),
        "name": obj.get("n", ""),
        "turnedOn": bool(state),
        "mode": mode if mode is not None else LOCAL_SENTINEL,
        "severity": severity,
        "severityDesc": _severity_desc(severity),
        "localControl": {
            "mode": True,
        },
        "local": {
            "typeCode": obj.get("t"),
            "flags": obj.get("f"),
            "state": _state_map(obj, "st"),
            "settings": _state_map(obj, "s"),
        },
    }


def _map_alarm(obj: dict[str, Any]) -> dict[str, Any]:
    severity = _clean_int(obj.get("sev"))
    return {
        "id": obj.get("i"),
        "type": "alarm",
        "name": obj.get("n", ""),
        "alarm": (_clean_number(_state(obj, "p1")) or 0) > 0,
        "severity": severity,
        "severityDesc": _severity_desc(severity),
        "local": {
            "typeCode": obj.get("t"),
            "flags": obj.get("f"),
            "state": _state_map(obj, "st"),
            "settings": _state_map(obj, "s"),
        },
    }


def normalize_local_device_info(
    obj_state: dict[str, Any],
    device_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Convert local UI API state into the cloud-shaped integration model."""

    severity = _clean_int(obj_state.get("deviceSeverity"))
    local: dict[str, Any] = {
        "available": True,
        "deviceFlags": obj_state.get("deviceFlags"),
        "deviceSeverity": severity,
        "simSignal": _clean_number(obj_state.get("simSignal")),
        "simBalance": _clean_number(obj_state.get("simBalance")),
        "curves": obj_state.get("curves", []),
        "hModes": obj_state.get("hModes", []),
        "scheds": obj_state.get("scheds", []),
        "objectState": {
            key: obj_state.get(key, []) for key in ("envs", "heaters", "engs", "alarms")
        },
        "deviceState": _safe_device_state(device_state),
    }

    if "securityArmed" in obj_state:
        local["securityArmed"] = bool(obj_state["securityArmed"])

    data = {
        "heaters": [_map_heater(obj) for obj in obj_state.get("heaters", [])],
        "envs": [_map_env(obj) for obj in obj_state.get("envs", [])],
        "engs": [_map_eng(obj) for obj in obj_state.get("engs", [])],
        "alarms": [_map_alarm(obj) for obj in obj_state.get("alarms", [])],
        "dataActual": True,
        "severity": severity,
        "severityDesc": _severity_desc(severity),
        "local": local,
    }

    gsm_rssi = _clean_number(local["deviceState"].get("gsmRssi"))
    gsm_balance = _clean_number(local["deviceState"].get("gsmBalance"))
    if gsm_rssi is not None:
        local["gsmRssi"] = gsm_rssi
    if gsm_balance is not None:
        local["gsmBalance"] = gsm_balance

    return data


def _merge_list(
    cloud_items: list[dict[str, Any]],
    local_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    result = [copy.deepcopy(item) for item in cloud_items]
    by_id = {
        item.get("id"): item
        for item in result
        if isinstance(item, dict) and item.get("id") is not None
    }

    for local_item in local_items:
        local_id = local_item.get("id")
        if local_id in by_id:
            merged = by_id[local_id]
            for key, value in local_item.items():
                if key in ("local", "localControl", "minTemp", "maxTemp"):
                    merged[key] = copy.deepcopy(value)
                elif key not in merged or merged[key] is None:
                    merged[key] = copy.deepcopy(value)
            continue

        result.append(copy.deepcopy(local_item))

    return result


def merge_local_device_info(
    cloud_data: dict[str, Any] | None,
    local_data: dict[str, Any] | None,
) -> dict[str, Any]:
    """Merge optional local data into cloud-shaped data."""

    if cloud_data is None:
        return copy.deepcopy(local_data or {})
    if local_data is None:
        return copy.deepcopy(cloud_data)

    result = copy.deepcopy(cloud_data)

    for key in ("heaters", "envs", "engs", "alarms"):
        result[key] = _merge_list(result.get(key, []), local_data.get(key, []))

    result["local"] = copy.deepcopy(local_data.get("local", {}))
    if result.get("severity") is None:
        result["severity"] = local_data.get("severity")
        result["severityDesc"] = local_data.get("severityDesc")
    result.setdefault("dataActual", local_data.get("dataActual", True))
    return result


class MhHybridApiClient:
    """Cloud client enriched with optional local UI API data."""

    def __init__(
        self,
        *,
        cloud_client: MhApiClient,
        local_client: LocalApiClient | None = None,
        cloud_poll_interval: int = DEFAULT_CLOUD_POLL_INTERVAL,
        local_poll_interval: int = DEFAULT_LOCAL_POLL_INTERVAL,
    ) -> None:
        self.cloud = cloud_client
        self.local = local_client
        self._cloud_poll_interval = cloud_poll_interval
        self._local_poll_interval = local_poll_interval
        self._cloud_cache: dict[str, Any] | None = None
        self._local_cache: dict[str, Any] | None = None
        self._cloud_updated_at = 0.0
        self._local_updated_at = 0.0

    async def async_get_devices(self) -> dict[str, Any]:
        """Get cloud devices."""

        return await self.cloud.async_get_devices()

    async def async_get_device_info(self, *, device_id: int | None = None) -> dict:
        """Poll cloud and optional local data."""

        now = time.monotonic()
        cloud_error = None
        try:
            cloud_data = await self._get_cloud_data(now, device_id=device_id)
        except Exception as ex:  # pylint: disable=broad-except
            cloud_error = ex
            cloud_data = None
            _LOGGER.warning("Cloud MY HEAT API unavailable: %s", ex)

        local_data = await self._get_local_data(now)

        if cloud_data is None and local_data is None:
            if cloud_error is not None:
                raise cloud_error
            raise LocalResponseError(
                "Both cloud and local MY HEAT APIs are unavailable"
            )

        return merge_local_device_info(cloud_data, local_data)

    async def _get_cloud_data(
        self,
        now: float,
        *,
        device_id: int | None,
    ) -> dict[str, Any] | None:
        if device_id is not None:
            return await self.cloud.async_get_device_info(device_id=device_id)

        if (
            self._cloud_cache is None
            or now - self._cloud_updated_at >= self._cloud_poll_interval
        ):
            self._cloud_cache = await self.cloud.async_get_device_info()
            self._cloud_updated_at = now

        return self._cloud_cache

    async def _get_local_data(self, now: float) -> dict[str, Any] | None:
        if self.local is None:
            return None

        if (
            self._local_cache is not None
            and now - self._local_updated_at < self._local_poll_interval
        ):
            return self._local_cache

        try:
            obj_state = await self.local.async_get_obj_state()
            try:
                device_state = await self.local.async_get_state()
            except LocalApiError, asyncio.TimeoutError:
                device_state = {}

            self._local_cache = normalize_local_device_info(obj_state, device_state)
            self._local_updated_at = now
            return self._local_cache
        except (LocalApiError, asyncio.TimeoutError) as ex:
            self._local_cache = None
            _LOGGER.warning("Local MY HEAT API unavailable: %s", ex)
            return None

    def _invalidate_cloud(self) -> None:
        self._cloud_cache = None
        self._cloud_updated_at = 0.0

    def _invalidate_local(self) -> None:
        self._local_cache = None
        self._local_updated_at = 0.0

    async def async_set_env_goal(
        self,
        *,
        obj_id: int,
        goal: int | float | None,
        device_id: int | None = None,
        change_mode: bool = False,
    ) -> None:
        if self.local is not None and self.local.has_env(obj_id):
            await self.local.async_set_env_goal(
                obj_id=obj_id,
                goal=goal,
                device_id=device_id,
                change_mode=change_mode,
            )
            self._invalidate_local()
            return

        kwargs = {"obj_id": obj_id, "goal": goal}
        if device_id is not None:
            kwargs["device_id"] = device_id
        if change_mode:
            kwargs["change_mode"] = change_mode
        await self.cloud.async_set_env_goal(**kwargs)
        self._invalidate_cloud()

    async def async_set_env_curve(
        self,
        *,
        obj_id: int,
        curve: int,
        device_id: int | None = None,
        change_mode: bool = False,
    ) -> None:
        if self.local is not None and self.local.has_env(obj_id):
            await self.local.async_set_env_curve(
                obj_id=obj_id,
                curve=curve,
                device_id=device_id,
                change_mode=change_mode,
            )
            self._invalidate_local()
            return

        kwargs = {"obj_id": obj_id, "curve": curve}
        if device_id is not None:
            kwargs["device_id"] = device_id
        if change_mode:
            kwargs["change_mode"] = change_mode
        await self.cloud.async_set_env_curve(**kwargs)
        self._invalidate_cloud()

    async def async_set_eng_goal(
        self,
        *,
        obj_id: int,
        goal: int | float,
        device_id: int | None = None,
        change_mode: bool = False,
    ) -> None:
        if self.local is not None and self.local.has_eng(obj_id):
            await self.local.async_set_eng_goal(
                obj_id=obj_id,
                goal=goal,
                device_id=device_id,
                change_mode=change_mode,
            )
            self._invalidate_local()
            return

        kwargs = {"obj_id": obj_id, "goal": goal}
        if device_id is not None:
            kwargs["device_id"] = device_id
        if change_mode:
            kwargs["change_mode"] = change_mode
        await self.cloud.async_set_eng_goal(**kwargs)
        self._invalidate_cloud()

    async def async_set_heater_enabled(self, *, obj_id: int, enabled: bool) -> None:
        if self.local is None or not self.local.has_heater(obj_id):
            raise LocalValidationError("Local heater control is not available")

        await self.local.async_set_heater_enabled(obj_id=obj_id, enabled=enabled)
        self._invalidate_local()

    async def async_set_heating_mode(
        self,
        *,
        device_id: int | None = None,
        mode_id: int | None = None,
        schedule_id: int | None = None,
    ) -> None:
        if (
            self.local is not None
            and (
                mode_id is None or mode_id == -1 or self.local.has_heating_mode(mode_id)
            )
            and (
                schedule_id is None
                or schedule_id == -1
                or self.local.has_schedule(schedule_id)
            )
        ):
            await self.local.async_set_heating_mode(
                device_id=device_id,
                mode_id=mode_id,
                schedule_id=schedule_id,
            )
            self._invalidate_local()
            return

        kwargs = {}
        if device_id is not None:
            kwargs["device_id"] = device_id
        if mode_id is not None:
            kwargs["mode_id"] = mode_id
        if schedule_id is not None:
            kwargs["schedule_id"] = schedule_id
        await self.cloud.async_set_heating_mode(**kwargs)
        self._invalidate_cloud()

    async def async_set_security_mode(
        self,
        *,
        mode: bool,
        device_id: int | None = None,
    ) -> None:
        if self.local is not None and self.local.supports_security():
            await self.local.async_set_security_mode(mode=mode, device_id=device_id)
            self._invalidate_local()
            return

        kwargs = {"mode": mode}
        if device_id is not None:
            kwargs["device_id"] = device_id
        await self.cloud.async_set_security_mode(**kwargs)
        self._invalidate_cloud()
