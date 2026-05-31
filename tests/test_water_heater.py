"""Test MyHeat water heater entities."""

from unittest.mock import call, patch

from homeassistant.components.water_heater import (
    ATTR_OPERATION_MODE,
    DOMAIN as WATER_HEATER_DOMAIN,
    SERVICE_SET_OPERATION_MODE,
    SERVICE_SET_TEMPERATURE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.const import ATTR_ENTITY_ID, ATTR_TEMPERATURE

from .helpers import setup_mock_entry, state_by_name


async def test_water_heater_entities(hass, bypass_get_device_info):
    """Test water heater entities are created from non-room envs."""
    await setup_mock_entry(hass)

    assert len(hass.states.async_entity_ids(WATER_HEATER_DOMAIN)) == 2

    boiler = state_by_name(hass, WATER_HEATER_DOMAIN, "test_device Бойлер")
    assert boiler.state == STATE_ON
    assert boiler.attributes["current_temperature"] == 46.7
    assert boiler.attributes["temperature"] == 45
    assert boiler.attributes["is_burning"] is False

    circuit = state_by_name(hass, WATER_HEATER_DOMAIN, "test_device Контур отопления")
    assert circuit.state == STATE_OFF
    assert circuit.attributes["current_temperature"] == 56
    assert circuit.attributes["temperature"] == 0.0


async def test_water_heater_services(hass, bypass_get_device_info):
    """Test water heater services call MyHeat API methods."""
    await setup_mock_entry(hass)
    boiler = state_by_name(hass, WATER_HEATER_DOMAIN, "test_device Бойлер")

    with patch("custom_components.myheat.MhApiClient.async_set_env_goal") as goal_func:
        await hass.services.async_call(
            WATER_HEATER_DOMAIN,
            SERVICE_SET_TEMPERATURE,
            service_data={
                ATTR_ENTITY_ID: boiler.entity_id,
                ATTR_TEMPERATURE: 44.5,
            },
            blocking=True,
        )
        assert goal_func.call_args == call(obj_id=21, goal=44.5)

        goal_func.reset_mock()

        await hass.services.async_call(
            WATER_HEATER_DOMAIN,
            SERVICE_TURN_OFF,
            service_data={ATTR_ENTITY_ID: boiler.entity_id},
            blocking=True,
        )
        assert goal_func.call_args == call(obj_id=21, goal=None)

        goal_func.reset_mock()

        await hass.services.async_call(
            WATER_HEATER_DOMAIN,
            SERVICE_TURN_ON,
            service_data={ATTR_ENTITY_ID: boiler.entity_id},
            blocking=True,
        )
        assert goal_func.call_args == call(obj_id=21, goal=45)

        goal_func.reset_mock()

        await hass.services.async_call(
            WATER_HEATER_DOMAIN,
            SERVICE_SET_OPERATION_MODE,
            service_data={
                ATTR_ENTITY_ID: boiler.entity_id,
                ATTR_OPERATION_MODE: STATE_OFF,
            },
            blocking=True,
        )
        assert goal_func.call_args == call(obj_id=21, goal=None)
