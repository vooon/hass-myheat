"""Tests for the local MY HEAT UI API client."""

from copy import deepcopy

import pytest

from custom_components.myheat.const import LOCAL_SENTINEL
from custom_components.myheat.hybrid_api import normalize_local_device_info
from custom_components.myheat.local_api import (
    LocalApiClient,
    LocalAuthError,
    LocalResponseError,
    LocalVerificationError,
)

from .const import MOCK_LOCAL_GET_STATE, MOCK_LOCAL_OBJ_STATE


class FakeHeaders(dict):
    """Small subset of aiohttp response headers used by the client."""

    def getall(self, key, default=None):
        value = self.get(key, default or [])
        if isinstance(value, list):
            return value
        return [value]


class FakeResponse:
    def __init__(self, payload, *, status=200, headers=None):
        self._payload = payload
        self.status = status
        self.headers = FakeHeaders(headers or {})

    async def json(self, *, content_type=None):  # pylint: disable=unused-argument
        return self._payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    async def post(self, url, *, headers, json):
        self.requests.append(
            {
                "url": url,
                "headers": headers,
                "json": json,
            }
        )
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def local_client(session) -> LocalApiClient:
    return LocalApiClient(
        host="192.0.2.10",
        username="myheat",
        password="myheat",
        session=session,
    )


async def test_local_login_stores_cookie_and_sends_it():
    session = FakeSession(
        [
            FakeResponse(
                {"status": True},
                headers={"Set-Cookie": "EspSessId=session-id; Max-Age=86400; Path=/;"},
            ),
            FakeResponse(MOCK_LOCAL_OBJ_STATE),
        ]
    )
    client = local_client(session)

    await client.async_login()
    assert client.authenticated

    await client.async_get_obj_state()
    assert "Cookie" not in session.requests[0]["headers"]
    assert session.requests[1]["headers"]["Cookie"] == "EspSessId=session-id"


async def test_local_failed_login_raises_auth_error():
    session = FakeSession([FakeResponse({"status": False})])
    client = local_client(session)

    with pytest.raises(LocalAuthError):
        await client.async_login()


async def test_normalize_local_device_info_maps_objects_and_sanitizes_regkey():
    data = normalize_local_device_info(MOCK_LOCAL_OBJ_STATE, MOCK_LOCAL_GET_STATE)

    assert data["dataActual"] is True
    assert data["severity"] == 1
    assert data["local"]["simSignal"] == 71
    assert data["local"]["gsmBalance"] == 137.7
    assert "regkey" not in data["local"]["deviceState"]

    room = data["envs"][0]
    assert room["id"] == 67
    assert room["type"] == "room_temperature"
    assert room["value"] == 22.5
    assert room["target"] == 23.5
    assert room["localControl"]["curve"] is True

    unavailable = data["envs"][1]
    assert unavailable["value"] is None

    heater = data["heaters"][0]
    assert heater["disabled"] is False
    assert heater["flowTemp"] == 51
    assert heater["localControl"]["enabled"] is True


async def test_local_obj_state_schema_rejects_missing_required_arrays():
    session = FakeSession([FakeResponse({"heaters": []})])
    client = local_client(session)
    client._session_id = "session-id"  # pylint: disable=protected-access

    with pytest.raises(LocalResponseError):
        await client.async_get_obj_state()


async def test_local_heater_enabled_payload_and_verification():
    obj_state = deepcopy(MOCK_LOCAL_OBJ_STATE)
    updated_state = deepcopy(MOCK_LOCAL_OBJ_STATE)
    updated_state["heaters"][0]["s"]["p3013"] = "1"
    session = FakeSession(
        [
            FakeResponse({"status": 1}),
            FakeResponse(updated_state),
        ]
    )
    client = local_client(session)
    client._session_id = "session-id"  # pylint: disable=protected-access
    client._obj_state = obj_state  # pylint: disable=protected-access

    await client.async_set_heater_enabled(obj_id=45, enabled=False)

    assert session.requests[0]["json"] == {
        "id": 45,
        "target": "heater",
        "value": 1,
    }
    assert session.requests[0]["headers"]["Cookie"] == "EspSessId=session-id"


async def test_local_env_target_payload_and_verification():
    updated_state = deepcopy(MOCK_LOCAL_OBJ_STATE)
    updated_state["envs"][0]["s"]["p3008"] = "25.1"
    session = FakeSession(
        [
            FakeResponse({"status": 1}),
            FakeResponse(updated_state),
        ]
    )
    client = local_client(session)
    client._session_id = "session-id"  # pylint: disable=protected-access
    client._obj_state = deepcopy(
        MOCK_LOCAL_OBJ_STATE
    )  # pylint: disable=protected-access

    await client.async_set_env_goal(obj_id=67, goal=25.1)

    assert session.requests[0]["json"] == {
        "id": 67,
        "target": "env",
        "value": 25.1,
        "curve": LOCAL_SENTINEL,
    }


async def test_local_env_curve_payload_and_verification():
    updated_state = deepcopy(MOCK_LOCAL_OBJ_STATE)
    updated_state["envs"][0]["s"]["p3022"] = "1"
    session = FakeSession(
        [
            FakeResponse({"status": 1}),
            FakeResponse(updated_state),
        ]
    )
    client = local_client(session)
    client._session_id = "session-id"  # pylint: disable=protected-access
    client._obj_state = deepcopy(
        MOCK_LOCAL_OBJ_STATE
    )  # pylint: disable=protected-access

    await client.async_set_env_curve(obj_id=67, curve=1)

    assert session.requests[0]["json"] == {
        "id": 67,
        "target": "env",
        "value": LOCAL_SENTINEL,
        "curve": 1,
    }


async def test_local_eng_goal_payload_and_verification():
    updated_state = deepcopy(MOCK_LOCAL_OBJ_STATE)
    updated_state["engs"][0]["s"]["p3008"] = "1"
    session = FakeSession(
        [
            FakeResponse({"status": 1}),
            FakeResponse(updated_state),
        ]
    )
    client = local_client(session)
    client._session_id = "session-id"  # pylint: disable=protected-access
    client._obj_state = deepcopy(
        MOCK_LOCAL_OBJ_STATE
    )  # pylint: disable=protected-access

    await client.async_set_eng_goal(obj_id=123, goal=1)

    assert session.requests[0]["json"] == {
        "id": 123,
        "target": "eng",
        "value": 1,
    }


async def test_local_heating_mode_payload_refreshes_state():
    session = FakeSession(
        [
            FakeResponse({"status": 1}),
            FakeResponse(MOCK_LOCAL_OBJ_STATE),
        ]
    )
    client = local_client(session)
    client._session_id = "session-id"  # pylint: disable=protected-access
    client._obj_state = deepcopy(
        MOCK_LOCAL_OBJ_STATE
    )  # pylint: disable=protected-access

    await client.async_set_heating_mode(mode_id=1)

    assert session.requests[0]["json"] == {
        "action": "setHeatingMode",
        "mode": 1,
        "schedule": -1,
    }


async def test_local_write_verification_mismatch_raises():
    session = FakeSession(
        [
            FakeResponse({"status": 1}),
            FakeResponse(MOCK_LOCAL_OBJ_STATE),
        ]
    )
    client = local_client(session)
    client._session_id = "session-id"  # pylint: disable=protected-access
    client._obj_state = deepcopy(
        MOCK_LOCAL_OBJ_STATE
    )  # pylint: disable=protected-access

    with pytest.raises(LocalVerificationError):
        await client.async_set_heater_enabled(obj_id=45, enabled=False)
