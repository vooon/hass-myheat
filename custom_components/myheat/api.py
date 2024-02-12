"""Sample API Client."""

import asyncio
import logging
import socket
from typing import Any, Union

import aiohttp
import voluptuous as vol

from .const import VERSION

TIMEOUT = 10

_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "User-Agent": f"homeassistant-myheat/{VERSION}",
}

RPC_ENDPOINT = "https://my.myheat.net/api/request/"

RPC_SCHEMA = vol.Schema(
    {
        vol.Required("err"): int,
        vol.Optional("refreshPage"): bool,
        vol.Optional("data"): vol.Any(
            # getDevices
            vol.Schema(
                {
                    "devices": [
                        vol.Schema(
                            {
                                "id": int,
                                "name": str,
                                "severity": int,
                                "severityDesc": str,
                            },
                            extra=vol.ALLOW_EXTRA,
                        ),
                    ],
                },
                extra=vol.ALLOW_EXTRA,
            ),
            # getDeviceInfo
            vol.Schema(
                {
                    "heaters": [
                        vol.Schema(
                            {
                                "id": int,
                                "name": str,
                                "disabled": bool,
                                "flowTemp": float,
                                "returnTemp": float,
                                "pressure": vol.Any(None, float),
                                "targetTemp": float,
                                "burnerHeating": bool,
                                "burnerWater": bool,
                                "modulation": int,
                            },
                            extra=vol.ALLOW_EXTRA,
                        ),
                    ],
                    "envs": [
                        vol.Schema(
                            {
                                "id": int,
                                "type": str,
                                "name": str,
                                "value": float,
                                "target": vol.Any(None, float),
                                "demand": bool,
                                "severity": int,
                                "severityDesc": str,
                            },
                            extra=vol.ALLOW_EXTRA,
                        ),
                    ],
                    "engs": [
                        vol.Schema(
                            {
                                "id": int,
                                "type": str,
                                "name": str,
                                "turnedOn": bool,
                                "severity": int,
                                "severityDesc": str,
                            },
                            extra=vol.ALLOW_EXTRA,
                        ),
                    ],
                    "alarms": dict,
                    "dataActual": bool,
                    "severity": int,
                    "severityDesc": str,
                    "weatherTemp": float,
                    "city": str,
                },
                extra=vol.ALLOW_EXTRA,
            ),
            # nothing more yet documented
        ),
    },
    extra=vol.ALLOW_EXTRA,
)


class RPCError(Exception):
    """API returned error"""

    code: int
    _full_response: dict[str, Any]

    def __init__(self, resp: dict[str, Any]):
        self.code = resp["err"]
        self._full_response = resp

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} code: {self.code}>"


class MhApiClient:
    """API helper to manipulate with myheat.net cloud"""

    def __init__(
        self,
        *,
        username: str,
        api_key: str,
        device_id: int,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._username: str = username
        self._api_key: str = api_key
        self._device_id: int = device_id
        self._session: aiohttp.ClientSession = session

    async def async_get_devices(self) -> dict:
        """Get available devices"""
        return await self.rpc("getDevices")

    async def async_get_device_info(self, *, device_id: int | None = None) -> dict:
        """Get device state and objects"""
        return await self.rpc("getDeviceInfo", deviceId=device_id)

    async def async_set_env_goal(
        self,
        *,
        obj_id: int,
        goal: Union[int, float],
        device_id: int | None = None,
        change_mode: bool = False,
    ) -> None:
        """Set goal for environment"""
        await self.rpc(
            "setEnvGoal",
            deviceId=device_id,
            objId=obj_id,
            goal=goal,
            changeMode=change_mode and 1 or 0,
        )

    async def async_set_env_curve(
        self,
        *,
        obj_id: int,
        curve: int,
        device_id: int | None = None,
        change_mode: bool = False,
    ) -> None:
        """Set goal curve for environment"""
        await self.rpc(
            "setEnvCurve",
            deviceId=device_id,
            objId=obj_id,
            curve=curve,
            changeMode=change_mode and 1 or 0,
        )

    async def async_set_eng_goal(
        self,
        *,
        obj_id: int,
        goal: Union[int, float],
        device_id: int | None = None,
        change_mode: bool = False,
    ) -> None:
        """Set goal for engineering component"""
        await self.rpc(
            "setEngGoal",
            deviceId=device_id,
            objId=obj_id,
            goal=goal,
            changeMode=change_mode and 1 or 0,
        )

    async def async_set_heating_mode(
        self,
        *,
        device_id: int | None = None,
        mode_id: int | None = None,
        schedule_id: int | None = None,
    ) -> None:
        """Set heating mode.

        Should be only one ID set: Mode or Schedule
        Value of 0 resets mode.
        """

        kvs = {}
        if mode_id is not None:
            kvs["modeId"] = mode_id
        if schedule_id is not None:
            kvs["scheduleId"] = schedule_id

        await self.rpc("setHeatingMode", deviceId=device_id, **kvs)

    async def async_set_security_mode(
        self,
        *,
        mode: bool,
        device_id: int | None = None,
    ) -> None:
        """Set security alarm mode (on/off)"""
        await self.rpc("setSecurityMode", deviceId=device_id, mode=mode and 1 or 0)

    async def rpc(self, action: str, **kwargs: dict) -> dict:
        """Get information from the API."""

        url = RPC_ENDPOINT

        kwargs["action"] = action
        kwargs["login"] = self._username
        kwargs["key"] = self._api_key

        # If deviceId is passed, and it is None => use the id stored in the instance
        if kwargs.get("deviceId", 1) is None:
            kwargs["deviceId"] = self._device_id

        try:
            async with asyncio.timeout(TIMEOUT):
                response = await self._session.post(url, headers=HEADERS, json=kwargs)
                data = await response.json()

                _LOGGER.debug("Data: %s", data)

                data = RPC_SCHEMA(data)
                if data["err"] != 0:
                    raise RPCError(data)

                return data.get("data", {})

        except (asyncio.TimeoutError, asyncio.CancelledError) as ex:
            _LOGGER.exception(
                "Timeout error fetching information from %s - %s",
                url,
                ex,
            )
            raise
        except (KeyError, TypeError) as ex:
            _LOGGER.exception(
                "Error parsing information from %s - %s",
                url,
                ex,
            )
            raise
        except (aiohttp.ClientError, socket.gaierror) as ex:
            _LOGGER.exception(
                "Error fetching information from %s - %s",
                url,
                ex,
            )
            raise
        except Exception as ex:  # pylint: disable=broad-except
            _LOGGER.exception("Something really wrong happened! - %s", ex)
            raise

        raise AssertionError("reached unreachable code")
