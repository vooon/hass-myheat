"""Sample API Client."""
import asyncio
import logging
import socket

import aiohttp
import async_timeout

from .const import VERSION

TIMEOUT = 10


_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "User-Agent": f"homeassistant-myheat/{VERSION}",
}

RPC_ENDPOINT = "https://my.myheat.net/api/request/"


class MhApiClient:
    """
    API helper to manipulate with myheat.net cloud
    """

    def __init__(
        self, username: str, password: str, session: aiohttp.ClientSession
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._passeword = password
        self._session = session

    async def async_get_devices(self) -> dict:
        """Get available devices"""
        return await self.rpc("getDevices")

    async def async_get_device_info(self, device_id: int) -> dict:
        """Get device state and objects"""
        return await self.rpc("getDeviceInfo", deviceId=device_id)

    async def async_set_env_goal(
        self, device_id: int, obj_id: int, goal: int, change_mode: bool = False
    ) -> None:
        """Set goal for environment"""
        await self.rpc(
            "setEnvGoal",
            deviceId=device_id,
            objId=obj_id,
            changeMode=change_mode and 1 or 0,
        )

    async def async_set_env_curve(
        self, device_id: int, obj_id: int, curve: int, change_mode: bool = False
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
        self, device_id: int, obj_id: int, goal: int, change_mode: bool = False
    ) -> None:
        """Set goal for engineering component"""
        await self.rpc(
            "setEngGoal",
            deviceId=device_id,
            objId=obj_id,
            changeMode=change_mode and 1 or 0,
        )

    async def async_set_heating_mode(
        self, device_id: int, mode_id: int = None, schedule_id: int = None
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

    async def async_set_security_mode(self, device_id: int, mode: bool) -> None:
        """Set security alarm mode (on/off)"""
        await self.rpc("setSecurityMode", deviceId=device_id, mode=mode and 1 or 0)

    async def rpc(self, action: str, **kwargs: dict) -> dict:
        """Get information from the API."""

        url = RPC_ENDPOINT

        kwargs["action"] = action
        kwargs["login"] = self._username
        kwargs["key"] = self._passeword

        try:
            async with async_timeout.timeout(TIMEOUT, loop=asyncio.get_event_loop()):
                response = await self._session.post(url, headers=HEADERS, json=kwargs)
                return await response.json()

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )
        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)
