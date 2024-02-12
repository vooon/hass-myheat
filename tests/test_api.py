"""Tests for MyHeat api."""

import asyncio

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import pytest

from custom_components.myheat.api import RPC_ENDPOINT, MhApiClient

from .const import MOCK_GET_DEVIDE_INFO, MOCK_GET_DEVIDES, MOCK_NO_ERR


def api_client(hass) -> MhApiClient:
    return MhApiClient(
        username="test_user",
        api_key="test_api_key",
        device_id=12,
        session=async_get_clientsession(hass),
    )


async def test_api_get_devices(
    hass,
    aioclient_mock,
):
    """Test API calls."""
    api = api_client(hass)

    aioclient_mock.post(RPC_ENDPOINT, json=MOCK_GET_DEVIDES)
    assert await api.async_get_devices() == MOCK_GET_DEVIDES["data"]


async def test_api_get_device_info(
    hass,
    aioclient_mock,
):
    """Test API calls."""
    api = api_client(hass)

    aioclient_mock.post(RPC_ENDPOINT, json=MOCK_GET_DEVIDE_INFO)
    assert await api.async_get_device_info() == MOCK_GET_DEVIDE_INFO["data"]


async def test_api_set(
    hass,
    aioclient_mock,
):
    """Test API calls."""
    api = api_client(hass)

    aioclient_mock.post(RPC_ENDPOINT, json=MOCK_NO_ERR)
    assert await api.async_set_env_goal(obj_id=21, goal=24) is None

    aioclient_mock.post(RPC_ENDPOINT, json=MOCK_NO_ERR)
    assert await api.async_set_env_curve(obj_id=21, curve=0) is None

    aioclient_mock.post(RPC_ENDPOINT, json=MOCK_NO_ERR)
    assert await api.async_set_eng_goal(obj_id=21, goal=-1) is None

    aioclient_mock.post(RPC_ENDPOINT, json=MOCK_NO_ERR)
    assert await api.async_set_heating_mode(mode_id=2) is None

    aioclient_mock.post(RPC_ENDPOINT, json=MOCK_NO_ERR)
    assert await api.async_set_heating_mode(mode_id=0, schedule_id=1) is None

    aioclient_mock.post(RPC_ENDPOINT, json=MOCK_NO_ERR)
    assert await api.async_set_security_mode(mode=True) is None


async def test_api_rpc_error_timeout(hass, aioclient_mock, caplog):
    """Test API calls."""
    api = api_client(hass)

    with pytest.raises(asyncio.TimeoutError):
        aioclient_mock.post(RPC_ENDPOINT, exc=asyncio.TimeoutError)
        assert await api.rpc("timeout") is None
        assert (
            len(caplog.record_tuples) == 1
            and "Timeout error fetching information from" in caplog.record_tuples[0][2]
        )


async def test_api_rpc_error_client(hass, aioclient_mock, caplog):
    """Test API calls."""
    api = api_client(hass)

    with pytest.raises(aiohttp.ClientError):
        aioclient_mock.post(RPC_ENDPOINT, exc=aiohttp.ClientError)
        assert await api.rpc("client_error") is None
        assert (
            len(caplog.record_tuples) == 1
            and "Error fetching information from" in caplog.record_tuples[0][2]
        )


async def test_api_rpc_error_unknown_exception(hass, aioclient_mock, caplog):
    """Test API calls."""
    api = api_client(hass)

    with pytest.raises(Exception):
        aioclient_mock.post(RPC_ENDPOINT, exc=Exception)
        assert await api.rpc("exc") is None
        assert (
            len(caplog.record_tuples) == 1
            and "Something really wrong happened!" in caplog.record_tuples[0][2]
        )


async def test_api_rpc_error_type_error(hass, aioclient_mock, caplog):
    """Test API calls."""
    api = api_client(hass)

    with pytest.raises(TypeError):
        aioclient_mock.post(RPC_ENDPOINT, exc=TypeError)
        assert await api.rpc("type_error") is None
        assert (
            len(caplog.record_tuples) == 1
            and "Error parsing information from" in caplog.record_tuples[0][2]
        )
