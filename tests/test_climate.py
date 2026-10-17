"""Test MyHeat climate entities."""

from unittest.mock import call, patch

from homeassistant.components.climate import (
    ATTR_HVAC_ACTION,
    ATTR_HVAC_MODE,
    ATTR_PRESET_MODE,
    DOMAIN as CLIMATE_DOMAIN,
    HVACAction,
    HVACMode,
    PRESET_HOME,
    PRESET_NONE,
    PRESET_SLEEP,
    SERVICE_SET_HVAC_MODE,
    SERVICE_SET_PRESET_MODE,
    SERVICE_SET_TEMPERATURE,
)
from homeassistant.const import ATTR_ENTITY_ID, ATTR_TEMPERATURE
from homeassistant.core import State
from pytest_homeassistant_custom_component.common import mock_restore_cache

from .helpers import setup_mock_entry, state_by_name


async def test_climate_entities(hass, bypass_get_device_info):
    """Test climate entities are created from room and floor temperature envs."""
    await setup_mock_entry(hass)

    assert len(hass.states.async_entity_ids(CLIMATE_DOMAIN)) == 5

    cafe = state_by_name(hass, CLIMATE_DOMAIN, "test_device Кафе")
    assert cafe.state == HVACMode.HEAT
    assert cafe.attributes["current_temperature"] == 24.8
    assert cafe.attributes["temperature"] == 23
    assert cafe.attributes[ATTR_HVAC_ACTION] == HVACAction.IDLE

    floor = state_by_name(hass, CLIMATE_DOMAIN, "test_device Теплый пол")
    assert floor.state == HVACMode.HEAT
    assert floor.attributes["current_temperature"] == 26.5
    assert floor.attributes["temperature"] == 27
    assert floor.attributes[ATTR_HVAC_ACTION] == HVACAction.HEATING

    accounting = state_by_name(hass, CLIMATE_DOMAIN, "test_device Бухгалтерия")
    assert accounting.state == HVACMode.OFF
    assert accounting.attributes["current_temperature"] == 29.8
    assert accounting.attributes["temperature"] is None
    assert accounting.attributes[ATTR_HVAC_ACTION] == HVACAction.OFF


async def test_climate_services(hass, bypass_get_device_info):
    """Test climate services call MyHeat API methods."""
    await setup_mock_entry(hass)
    cafe = state_by_name(hass, CLIMATE_DOMAIN, "test_device Кафе")

    with patch("custom_components.myheat.MhApiClient.async_set_env_goal") as goal_func:
        await hass.services.async_call(
            CLIMATE_DOMAIN,
            SERVICE_SET_TEMPERATURE,
            service_data={
                ATTR_ENTITY_ID: cafe.entity_id,
                ATTR_TEMPERATURE: 21.5,
            },
            blocking=True,
        )
        assert goal_func.call_args == call(obj_id=22, goal=21.5, change_mode=True)

        goal_func.reset_mock()

        await hass.services.async_call(
            CLIMATE_DOMAIN,
            SERVICE_SET_HVAC_MODE,
            service_data={
                ATTR_ENTITY_ID: cafe.entity_id,
                ATTR_HVAC_MODE: HVACMode.OFF,
            },
            blocking=True,
        )
        assert goal_func.call_args == call(obj_id=22, goal=None)

        goal_func.reset_mock()

        await hass.services.async_call(
            CLIMATE_DOMAIN,
            SERVICE_SET_HVAC_MODE,
            service_data={
                ATTR_ENTITY_ID: cafe.entity_id,
                ATTR_HVAC_MODE: HVACMode.HEAT,
            },
            blocking=True,
        )
        assert goal_func.call_args == call(obj_id=22, goal=23, change_mode=True)

    with patch(
        "custom_components.myheat.MhApiClient.async_set_heating_mode"
    ) as mode_func:
        await hass.services.async_call(
            CLIMATE_DOMAIN,
            SERVICE_SET_PRESET_MODE,
            service_data={
                ATTR_ENTITY_ID: cafe.entity_id,
                ATTR_PRESET_MODE: PRESET_HOME,
            },
            blocking=True,
        )
        assert mode_func.call_args == call(mode_id=1)

    # Heating mode is per device, so every climate entity shows it.
    for name in ("test_device Кафе", "test_device Теплый пол"):
        state = state_by_name(hass, CLIMATE_DOMAIN, name)
        assert state.attributes[ATTR_PRESET_MODE] == PRESET_HOME


async def test_climate_restore_preset(hass, bypass_get_device_info):
    """Test the last preset is restored, as the API does not report it."""
    mock_restore_cache(
        hass,
        [
            State(
                "climate.test_device_kafe",
                HVACMode.HEAT,
                {ATTR_PRESET_MODE: PRESET_SLEEP},
            )
        ],
    )
    await setup_mock_entry(hass)

    for state in hass.states.async_all(CLIMATE_DOMAIN):
        assert state.attributes[ATTR_PRESET_MODE] == PRESET_SLEEP


async def test_climate_default_preset(hass, bypass_get_device_info):
    """Test preset is none when nothing was set or restored."""
    await setup_mock_entry(hass)

    for state in hass.states.async_all(CLIMATE_DOMAIN):
        assert state.attributes[ATTR_PRESET_MODE] == PRESET_NONE
