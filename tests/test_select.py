"""Test MyHeat select entities for engineering components."""

from copy import deepcopy
from unittest.mock import call, patch

from homeassistant.components.select import (
    ATTR_OPTION,
    SERVICE_SELECT_OPTION,
)
from homeassistant.components.select import (
    DOMAIN as SELECT_DOMAIN,
)
from homeassistant.const import ATTR_ENTITY_ID

from .const import MOCK_GET_DEVICE_INFO
from .helpers import setup_mock_entry, state_by_name


async def test_eng_select_entities(hass, bypass_get_device_info):
    """Test engineering components are exposed as mode selects."""
    await setup_mock_entry(hass)

    assert len(hass.states.async_entity_ids(SELECT_DOMAIN)) == 8

    # All mock engs report mode -1, which means automatic regulation.
    pump = state_by_name(hass, SELECT_DOMAIN, "test_device Насос магазин Mode")
    assert pump.state == "auto"
    assert pump.attributes["options"] == ["auto", "on", "off"]

    valve = state_by_name(
        hass, SELECT_DOMAIN, "test_device Клапан 3-ходовой Баня/Конвекторы Mode"
    )
    assert valve.state == "auto"


async def test_eng_select_explicit_modes(hass):
    """Test forced on/off goals are reflected in the selected option."""
    data = deepcopy(MOCK_GET_DEVICE_INFO["data"])
    data["engs"] = [
        {
            "id": 401,
            "type": "pump",
            "name": "Насос принудительно выключен",
            "turnedOn": False,
            "mode": 0,
            "severity": 1,
            "severityDesc": "Насос выключен.",
        },
        {
            "id": 402,
            "type": "pump",
            "name": "Насос принудительно включен",
            "turnedOn": True,
            "mode": 1,
            "severity": 1,
            "severityDesc": "Насос включен.",
        },
        {
            "id": 403,
            "type": "three_way_valve",
            "name": "Клапан авто",
            "turnedOn": False,
            "mode": -1,
            "severity": 1,
            "severityDesc": "Режим регулирования.",
        },
    ]

    with patch(
        "custom_components.myheat.MhApiClient.async_get_device_info",
        return_value=data,
    ):
        await setup_mock_entry(hass)

    assert len(hass.states.async_entity_ids(SELECT_DOMAIN)) == 3

    forced_off = state_by_name(
        hass, SELECT_DOMAIN, "test_device Насос принудительно выключен Mode"
    )
    assert forced_off.state == "off"

    forced_on = state_by_name(
        hass, SELECT_DOMAIN, "test_device Насос принудительно включен Mode"
    )
    assert forced_on.state == "on"

    auto = state_by_name(hass, SELECT_DOMAIN, "test_device Клапан авто Mode")
    assert auto.state == "auto"


async def test_eng_select_service(hass, bypass_get_device_info):
    """Test selecting an option calls setEngGoal with the right goal."""
    await setup_mock_entry(hass)

    pump = state_by_name(hass, SELECT_DOMAIN, "test_device Насос магазин Mode")

    with patch(
        "custom_components.myheat.MhApiClient.async_set_eng_goal"
    ) as eng_goal_func:
        await hass.services.async_call(
            SELECT_DOMAIN,
            SERVICE_SELECT_OPTION,
            service_data={
                ATTR_ENTITY_ID: pump.entity_id,
                ATTR_OPTION: "off",
            },
            blocking=True,
        )
        assert eng_goal_func.call_args == call(obj_id=40, goal=0)

        eng_goal_func.reset_mock()

        await hass.services.async_call(
            SELECT_DOMAIN,
            SERVICE_SELECT_OPTION,
            service_data={
                ATTR_ENTITY_ID: pump.entity_id,
                ATTR_OPTION: "on",
            },
            blocking=True,
        )
        assert eng_goal_func.call_args == call(obj_id=40, goal=1)

        eng_goal_func.reset_mock()

        await hass.services.async_call(
            SELECT_DOMAIN,
            SERVICE_SELECT_OPTION,
            service_data={
                ATTR_ENTITY_ID: pump.entity_id,
                ATTR_OPTION: "auto",
            },
            blocking=True,
        )
        assert eng_goal_func.call_args == call(obj_id=40, goal=-1)
