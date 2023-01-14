"""Tests for MyHeat api."""
import asyncio

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.myheat.api import RPC_ENDPOINT, MhApiClient

# Use data from api pdf
GET_DEVIDES = {
    "data": {
        "devices": [
            {
                "id": 12,
                "name": "У Моста",
                "city": "Новошешминск",
                "severity": 1,
                "severityDesc": "Система работает нормально.",
            },
            {
                "id": 10,
                "name": "Хорошее место",
                "city": "Новошешминск",
                "severity": 1,
                "severityDesc": "Система работает нормально.",
            },
        ]
    },
    "err": 0,
    "refreshPage": False,
}


GET_DEVIDE_INFO = {
    "data": {
        "heaters": [
            {
                "id": 13,
                "name": "Vaillant правый",
                "disabled": False,
                "flowTemp": 56,
                "returnTemp": 56,
                "pressure": 2.223,
                "targetTemp": 0,
                "burnerHeating": False,
                "burnerWater": False,
                "modulation": 0,
            },
            {
                "id": 37,
                "name": "Vaillant левый",
                "disabled": False,
                "flowTemp": 56,
                "returnTemp": 57,
                "pressure": 2.436,
                "targetTemp": 0,
                "burnerHeating": False,
                "burnerWater": False,
                "modulation": 0,
            },
        ],
        "envs": [
            {
                "id": 21,
                "type": "boiler_temperature",
                "name": "Бойлер",
                "value": 46.687,
                "target": 45,
                "demand": False,
                "severity": 1,
                "severityDesc": "Нормальное состояние.",
            },
            {
                "id": 22,
                "type": "room_temperature",
                "name": "Кафе",
                "value": 24.812,
                "target": 23,
                "demand": False,
                "severity": 1,
                "severityDesc": "Нормальное состояние.",
            },
            {
                "id": 24,
                "type": "circuit_temperature",
                "name": "Контур отопления",
                "value": 56,
                "target": None,
                "demand": False,
                "severity": 1,
                "severityDesc": "Нормальное состояние.",
            },
            {
                "id": 23,
                "type": "room_temperature",
                "name": "Магазин",
                "value": 24.187,
                "target": 23,
                "demand": False,
                "severity": 1,
                "severityDesc": "Нормальное состояние.",
            },
            {
                "id": 20,
                "type": "room_temperature",
                "name": "Бухгалтерия",
                "value": 29.812,
                "target": None,
                "demand": False,
                "severity": 1,
                "severityDesc": "Нормальное состояние.",
            },
            {
                "id": 19,
                "type": "room_temperature",
                "name": "Котельная",
                "value": 27.25,
                "target": None,
                "demand": False,
                "severity": 1,
                "severityDesc": "Нормальное состояние.",
            },
        ],
        "engs": [
            {
                "id": 40,
                "type": "pump",
                "name": "Насос магазин",
                "turnedOn": False,
                "severity": 1,
                "severityDesc": "Насос работает исправно.",
            },
            {
                "id": 41,
                "type": "pump",
                "name": "Насос бойлер",
                "turnedOn": False,
                "severity": 1,
                "severityDesc": "Насос работает исправно.",
            },
            {
                "id": 38,
                "type": "pump",
                "name": "Насос кафе",
                "turnedOn": False,
                "severity": 1,
                "severityDesc": "Насос работает исправно.",
            },
            {
                "id": 39,
                "type": "pump",
                "name": "Насос бухгалтерия",
                "turnedOn": False,
                "severity": 1,
                "severityDesc": "Насос работает исправно.",
            },
        ],
        "alarms": {},
        "dataActual": True,
        "severity": 1,
        "severityDesc": "Система работает нормально.",
        "weatherTemp": "-6.78999999999996",
        "city": "Новошешминск",
    },
    "err": 0,
    "refreshPage": False,
}

NO_ERR = {"err": 0, "refreshPage": False}


async def test_api(hass, aioclient_mock, caplog):
    """Test API calls."""

    api = MhApiClient("test_user", "test_api_key", async_get_clientsession(hass))

    aioclient_mock.post(RPC_ENDPOINT, json=GET_DEVIDES)
    assert await api.async_get_devices() == GET_DEVIDES

    aioclient_mock.post(RPC_ENDPOINT, json=GET_DEVIDE_INFO)
    assert await api.async_get_device_info(12) == GET_DEVIDE_INFO

    aioclient_mock.post(RPC_ENDPOINT, json=NO_ERR)
    assert await api.async_set_env_goal(12, 21, goal=24) is None

    aioclient_mock.post(RPC_ENDPOINT, json=NO_ERR)
    assert await api.async_set_env_curve(12, 21, curve=0) is None

    aioclient_mock.post(RPC_ENDPOINT, json=NO_ERR)
    assert await api.async_set_eng_goal(12, 21, goal=-1) is None

    aioclient_mock.post(RPC_ENDPOINT, json=NO_ERR)
    assert await api.async_set_heating_mode(12, mode_id=2) is None

    aioclient_mock.post(RPC_ENDPOINT, json=NO_ERR)
    assert await api.async_set_heating_mode(12, mode_id=0, schedule_id=1) is None

    aioclient_mock.post(RPC_ENDPOINT, json=NO_ERR)
    assert await api.async_set_security_mode(12, True) is None

    # In order to get 100% coverage, we need to test `api_wrapper` to test the code
    # that isn't already called by `async_get_data` and `async_set_title`. Because the
    # only logic that lives inside `api_wrapper` that is not being handled by a third
    # party library (aiohttp) is the exception handling, we also want to simulate
    # raising the exceptions to ensure that the function handles them as expected.
    # The caplog fixture allows access to log messages in tests. This is particularly
    # useful during exception handling testing since often the only action as part of
    # exception handling is a logging statement
    caplog.clear()
    aioclient_mock.post(RPC_ENDPOINT, exc=asyncio.TimeoutError)
    assert await api.rpc("timeout") is None
    assert (
        len(caplog.record_tuples) == 1
        and "Timeout error fetching information from" in caplog.record_tuples[0][2]
    )

    caplog.clear()
    aioclient_mock.post(RPC_ENDPOINT, exc=aiohttp.ClientError)
    assert await api.rpc("client_error") is None
    assert (
        len(caplog.record_tuples) == 1
        and "Error fetching information from" in caplog.record_tuples[0][2]
    )

    caplog.clear()
    aioclient_mock.post(RPC_ENDPOINT, exc=Exception)
    assert await api.rpc("exc") is None
    assert (
        len(caplog.record_tuples) == 1
        and "Something really wrong happened!" in caplog.record_tuples[0][2]
    )

    caplog.clear()
    aioclient_mock.post(RPC_ENDPOINT, exc=TypeError)
    assert await api.rpc("type_error") is None
    assert (
        len(caplog.record_tuples) == 1
        and "Error parsing information from" in caplog.record_tuples[0][2]
    )
