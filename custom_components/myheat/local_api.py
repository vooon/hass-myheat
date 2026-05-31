"""Local MY HEAT UI API client."""

from __future__ import annotations

import asyncio
from http.cookies import SimpleCookie
import logging
import socket
from typing import Any, Callable

import aiohttp
import voluptuous as vol

from .const import (
    DEFAULT_LOCAL_PROTOCOL,
    DEFAULT_LOCAL_REQUEST_TIMEOUT,
    LOCAL_SENTINEL,
)

_LOGGER = logging.getLogger(__package__)

LOCAL_LOGIN_SCHEMA = vol.Schema(
    {
        vol.Required("status"): bool,
    },
    extra=vol.ALLOW_EXTRA,
)

LOCAL_PARAM_MAP_SCHEMA = vol.Schema(dict, extra=vol.ALLOW_EXTRA)

LOCAL_OBJECT_SCHEMA = vol.Schema(
    {
        vol.Optional("n"): str,
        vol.Optional("i"): int,
        vol.Optional("t"): int,
        vol.Optional("f"): int,
        vol.Optional("sev"): int,
        vol.Optional("st", default=dict): LOCAL_PARAM_MAP_SCHEMA,
        vol.Optional("s", default=dict): LOCAL_PARAM_MAP_SCHEMA,
    },
    extra=vol.ALLOW_EXTRA,
)

LOCAL_CURVE_SCHEMA = vol.Schema(
    {
        vol.Required("i"): int,
        vol.Required("n"): str,
        vol.Required("d"): [vol.Any(int, float)],
    },
    extra=vol.ALLOW_EXTRA,
)

LOCAL_ID_NAME_SCHEMA = vol.Schema(
    {
        vol.Required("i"): int,
        vol.Required("n"): str,
    },
    extra=vol.ALLOW_EXTRA,
)

LOCAL_OBJ_STATE_SCHEMA = vol.Schema(
    {
        vol.Optional("deviceFlags"): vol.Any(int, float),
        vol.Optional("deviceSeverity"): vol.Any(int, float),
        vol.Optional("simSignal"): vol.Any(int, float),
        vol.Optional("simBalance"): vol.Any(int, float),
        vol.Required("envs"): [LOCAL_OBJECT_SCHEMA],
        vol.Optional("engs", default=list): [LOCAL_OBJECT_SCHEMA],
        vol.Optional("alarms", default=list): [LOCAL_OBJECT_SCHEMA],
        vol.Required("heaters"): [LOCAL_OBJECT_SCHEMA],
        vol.Optional("curves", default=list): [LOCAL_CURVE_SCHEMA],
        vol.Optional("hModes", default=list): [LOCAL_ID_NAME_SCHEMA],
        vol.Optional("scheds", default=list): [LOCAL_ID_NAME_SCHEMA],
        vol.Optional("hMode"): vol.Any(int, float),
        vol.Optional("sched"): vol.Any(int, float),
        vol.Optional("securityArmed"): vol.Any(bool, int),
    },
    extra=vol.ALLOW_EXTRA,
)

LOCAL_DEVICE_STATE_SCHEMA = vol.Schema(
    {
        vol.Optional("status"): vol.Any(int, bool),
        vol.Optional("inet"): vol.Any(str, int, bool),
        vol.Optional("serial"): vol.Any(str, int),
        vol.Optional("regkey"): vol.Any(str, int),
        vol.Optional("wifiSsid"): str,
        vol.Optional("gsmCarrier"): str,
        vol.Optional("gsmRssi"): vol.Any(str, int, float),
        vol.Optional("gsmBalance"): vol.Any(str, int, float),
    },
    extra=vol.ALLOW_EXTRA,
)

LOCAL_WRITE_SCHEMA = vol.Schema(
    {
        vol.Required("status"): int,
    },
    extra=vol.ALLOW_EXTRA,
)


class LocalApiError(Exception):
    """Base exception for the local UI API."""


class LocalAuthError(LocalApiError):
    """Local UI API credentials were rejected."""


class LocalResponseError(LocalApiError):
    """Local UI API returned an unexpected response."""


class LocalValidationError(LocalApiError):
    """Requested command is not valid for the discovered local objects."""


class LocalWriteError(LocalApiError):
    """Local UI API rejected a write command."""


class LocalVerificationError(LocalWriteError):
    """Local UI API accepted a write but refreshed state did not match."""


def _validate_response(
    schema: vol.Schema,
    data: dict[str, Any],
    endpoint: str,
) -> dict[str, Any]:
    try:
        return schema(data)
    except vol.Invalid as ex:
        raise LocalResponseError(
            f"Local API endpoint {endpoint} returned unexpected data"
        ) from ex


def _is_sentinel(value: Any) -> bool:
    try:
        return float(value) <= -16777215
    except (TypeError, ValueError):
        return False


def _clean_number(value: Any) -> float | None:
    if value is None or _is_sentinel(value):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
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
    except (TypeError, ValueError):
        return False


class LocalApiClient:
    """Client for the device-local `/api/*` JSON API."""

    def __init__(
        self,
        *,
        host: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
        protocol: str = DEFAULT_LOCAL_PROTOCOL,
        request_timeout: int = DEFAULT_LOCAL_REQUEST_TIMEOUT,
    ) -> None:
        self._base_url = f"{protocol}://{host.strip().rstrip('/')}"
        self._username = username
        self._password = password
        self._session = session
        self._request_timeout = request_timeout
        self._session_id: str | None = None
        self._obj_state: dict[str, Any] | None = None
        self._device_state: dict[str, Any] | None = None

    @property
    def authenticated(self) -> bool:
        """Return whether the local session cookie is available."""

        return self._session_id is not None

    def _url(self, endpoint: str) -> str:
        return f"{self._base_url}{endpoint}"

    def _headers(self, *, auth: bool) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if auth and self._session_id:
            headers["Cookie"] = f"EspSessId={self._session_id}"
        return headers

    async def _post(
        self,
        endpoint: str,
        payload: dict[str, Any],
        *,
        auth: bool = True,
    ) -> tuple[dict[str, Any], Any]:
        if auth:
            await self._ensure_authenticated()

        url = self._url(endpoint)
        try:
            async with asyncio.timeout(self._request_timeout):
                response = await self._session.post(
                    url,
                    headers=self._headers(auth=auth),
                    json=payload,
                )
                status = response.status
                data = await response.json(content_type=None)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            _LOGGER.exception("Timeout calling local API endpoint %s", endpoint)
            raise
        except (aiohttp.ClientError, socket.gaierror) as ex:
            _LOGGER.exception("Error calling local API endpoint %s: %s", endpoint, ex)
            raise LocalResponseError(f"Local API request failed: {endpoint}") from ex
        except ValueError as ex:
            _LOGGER.exception("Invalid JSON from local API endpoint %s", endpoint)
            raise LocalResponseError(f"Invalid local API JSON: {endpoint}") from ex

        if status < 200 or status >= 300:
            raise LocalResponseError(f"Local API endpoint {endpoint} returned {status}")
        if not isinstance(data, dict):
            raise LocalResponseError(f"Local API endpoint {endpoint} returned non-object")

        return data, response.headers

    async def _ensure_authenticated(self) -> None:
        if self._session_id is None:
            await self.async_login()

    def _store_session_cookie(self, headers: Any) -> None:
        for value in headers.getall("Set-Cookie", []):
            cookie = SimpleCookie()
            cookie.load(value)
            if morsel := cookie.get("EspSessId"):
                self._session_id = morsel.value
                return

    async def async_login(self) -> None:
        """Login and store the returned EspSessId cookie."""

        self._session_id = None
        data, headers = await self._post(
            "/api/login",
            {"login": self._username, "pswd": self._password},
            auth=False,
        )
        data = _validate_response(LOCAL_LOGIN_SCHEMA, data, "/api/login")
        if data.get("status") is not True:
            raise LocalAuthError("Invalid local MY HEAT credentials")

        self._store_session_cookie(headers)
        if self._session_id is None:
            raise LocalAuthError("Local MY HEAT login did not return EspSessId")

    async def async_get_obj_state(self) -> dict[str, Any]:
        """Fetch raw local object state."""

        data, _ = await self._post("/api/getObjState", {})
        data = _validate_response(LOCAL_OBJ_STATE_SCHEMA, data, "/api/getObjState")
        self._obj_state = data
        return data

    async def async_get_state(self) -> dict[str, Any]:
        """Fetch raw local device diagnostics."""

        data, _ = await self._post("/api/getState", {})
        data = _validate_response(LOCAL_DEVICE_STATE_SCHEMA, data, "/api/getState")
        self._device_state = data
        return data

    def _latest_obj_state(self) -> dict[str, Any]:
        if self._obj_state is None:
            raise LocalValidationError("Local object registry is not available yet")
        return self._obj_state

    def _find_object(self, collection: str, obj_id: int) -> dict[str, Any]:
        for obj in self._latest_obj_state().get(collection, []):
            if obj.get("i") == obj_id:
                return obj
        raise LocalValidationError(f"Local object {obj_id} not found in {collection}")

    def has_env(self, obj_id: int) -> bool:
        return self._has_object("envs", obj_id)

    def has_heater(self, obj_id: int) -> bool:
        return self._has_object("heaters", obj_id)

    def has_eng(self, obj_id: int) -> bool:
        return self._has_object("engs", obj_id)

    def _has_object(self, collection: str, obj_id: int) -> bool:
        if self._obj_state is None:
            return False
        return any(obj.get("i") == obj_id for obj in self._obj_state.get(collection, []))

    def has_curve(self, curve: int) -> bool:
        if self._obj_state is None:
            return False
        return any(item.get("i") == curve for item in self._obj_state.get("curves", []))

    def has_heating_mode(self, mode: int) -> bool:
        if self._obj_state is None:
            return False
        return any(item.get("i") == mode for item in self._obj_state.get("hModes", []))

    def has_schedule(self, schedule: int) -> bool:
        if self._obj_state is None:
            return False
        return any(item.get("i") == schedule for item in self._obj_state.get("scheds", []))

    def supports_security(self) -> bool:
        return self._obj_state is not None and "securityArmed" in self._obj_state

    async def _write_and_verify(
        self,
        payload: dict[str, Any],
        verify: Callable[[dict[str, Any]], bool] | None,
    ) -> None:
        data, _ = await self._post("/api/setObjState", payload)
        data = _validate_response(LOCAL_WRITE_SCHEMA, data, "/api/setObjState")
        if type(data.get("status")) is not int or data.get("status") != 1:
            raise LocalWriteError("Local API rejected the command")

        obj_state = await self.async_get_obj_state()
        if verify is not None and not verify(obj_state):
            raise LocalVerificationError("Local API state verification failed")

    async def async_set_env_goal(
        self,
        *,
        obj_id: int,
        goal: int | float | None,
        device_id: int | None = None,
        change_mode: bool = False,
    ) -> None:
        """Set local environment target."""

        del device_id, change_mode

        obj = self._find_object("envs", obj_id)
        if goal is not None:
            min_value = _clean_number(_setting(obj, "p3012"))
            max_value = _clean_number(_setting(obj, "p3011"))
            if min_value is not None and goal < min_value:
                raise LocalValidationError("Environment target is below local minimum")
            if max_value is not None and goal > max_value:
                raise LocalValidationError("Environment target is above local maximum")

        value = LOCAL_SENTINEL if goal is None else goal
        expected = None if goal is None else float(goal)

        def verify(state: dict[str, Any]) -> bool:
            updated = _find_obj_in_state(state, "envs", obj_id)
            target = _clean_number(_setting(updated, "p3008"))
            if expected is None:
                return target is None
            return target is not None and abs(target - expected) < 0.001

        await self._write_and_verify(
            {
                "id": obj_id,
                "target": "env",
                "value": value,
                "curve": LOCAL_SENTINEL,
            },
            verify,
        )

    async def async_set_env_curve(
        self,
        *,
        obj_id: int,
        curve: int,
        device_id: int | None = None,
        change_mode: bool = False,
    ) -> None:
        """Set local environment heating curve."""

        del device_id, change_mode

        obj = self._find_object("envs", obj_id)
        if not _is_nonzero(_setting(obj, "p3049")):
            raise LocalValidationError("Environment does not support local curves")
        if not self.has_curve(curve):
            raise LocalValidationError("Unknown local curve")

        def verify(state: dict[str, Any]) -> bool:
            updated = _find_obj_in_state(state, "envs", obj_id)
            return _clean_int(_setting(updated, "p3022")) == curve

        await self._write_and_verify(
            {
                "id": obj_id,
                "target": "env",
                "value": LOCAL_SENTINEL,
                "curve": curve,
            },
            verify,
        )

    async def async_set_eng_goal(
        self,
        *,
        obj_id: int,
        goal: int | float,
        device_id: int | None = None,
        change_mode: bool = False,
    ) -> None:
        """Set local engineering mode."""

        del device_id, change_mode

        self._find_object("engs", obj_id)
        value = LOCAL_SENTINEL if goal == -1 else int(goal)
        if value not in (LOCAL_SENTINEL, 0, 1):
            raise LocalValidationError("Unsupported local engineering mode")

        def verify(state: dict[str, Any]) -> bool:
            updated = _find_obj_in_state(state, "engs", obj_id)
            if "p3008" in _state_map(updated, "s"):
                current = _clean_int(_setting(updated, "p3008"))
                return (current is None and value == LOCAL_SENTINEL) or current == value
            current_state = _clean_int(_state(updated, "p4"))
            return current_state == value

        await self._write_and_verify(
            {
                "id": obj_id,
                "target": "eng",
                "value": value,
            },
            verify,
        )

    async def async_set_heater_enabled(self, *, obj_id: int, enabled: bool) -> None:
        """Enable or disable a local heater."""

        self._find_object("heaters", obj_id)
        value = 0 if enabled else 1

        def verify(state: dict[str, Any]) -> bool:
            updated = _find_obj_in_state(state, "heaters", obj_id)
            return _clean_int(_setting(updated, "p3013")) == value

        await self._write_and_verify(
            {
                "id": obj_id,
                "target": "heater",
                "value": value,
            },
            verify,
        )

    async def async_set_heating_mode(
        self,
        *,
        device_id: int | None = None,
        mode_id: int | None = None,
        schedule_id: int | None = None,
    ) -> None:
        """Set local heating mode or schedule."""

        del device_id

        mode = -1 if mode_id is None else mode_id
        schedule = -1 if schedule_id is None else schedule_id
        if mode != -1 and not self.has_heating_mode(mode):
            raise LocalValidationError("Unknown local heating mode")
        if schedule != -1 and not self.has_schedule(schedule):
            raise LocalValidationError("Unknown local schedule")

        def verify(state: dict[str, Any]) -> bool:
            has_mode = "hMode" in state
            has_schedule = "sched" in state
            if not has_mode and not has_schedule:
                return True
            return (
                (not has_mode or _clean_int(state.get("hMode")) == mode)
                and (not has_schedule or _clean_int(state.get("sched")) == schedule)
            )

        await self._write_and_verify(
            {
                "action": "setHeatingMode",
                "mode": mode,
                "schedule": schedule,
            },
            verify,
        )

    async def async_set_security_mode(
        self,
        *,
        mode: bool,
        device_id: int | None = None,
    ) -> None:
        """Arm or disarm local security when the field is discovered."""

        del device_id

        if not self.supports_security():
            raise LocalValidationError("Local security state is not available")

        def verify(state: dict[str, Any]) -> bool:
            return bool(state.get("securityArmed")) is mode

        await self._write_and_verify(
            {
                "action": "armSecurity" if mode else "disarmSecurity",
            },
            verify,
        )


def _find_obj_in_state(
    obj_state: dict[str, Any],
    collection: str,
    obj_id: int,
) -> dict[str, Any]:
    for obj in obj_state.get(collection, []):
        if obj.get("i") == obj_id:
            return obj
    raise LocalVerificationError(f"Object {obj_id} disappeared from {collection}")
