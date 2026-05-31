"""Test MyHeat sensors."""

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import UnitOfPressure, UnitOfTemperature

from .helpers import setup_mock_entry, state_by_name


async def test_sensor_entities(hass, bypass_get_device_info):
    """Test sensor entities are created from coordinator data."""
    await setup_mock_entry(hass)

    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 11

    weather = state_by_name(hass, SENSOR_DOMAIN, "test_device weatherTemp")
    assert weather.state == "-6.78999999999996"
    assert weather.attributes["city"] == "Новошешминск"
    assert weather.attributes["unit_of_measurement"] == UnitOfTemperature.CELSIUS

    flow_temp = state_by_name(
        hass, SENSOR_DOMAIN, "test_device Vaillant правый flowTemp"
    )
    assert flow_temp.state == "56"
    assert flow_temp.attributes["unit_of_measurement"] == UnitOfTemperature.CELSIUS

    pressure = state_by_name(
        hass, SENSOR_DOMAIN, "test_device Vaillant правый Pressure"
    )
    assert pressure.state == "2.223"
    assert pressure.attributes["unit_of_measurement"] == UnitOfPressure.BAR

    modulation = state_by_name(
        hass, SENSOR_DOMAIN, "test_device Vaillant правый Modulation"
    )
    assert modulation.state == "0"
    assert modulation.attributes["unit_of_measurement"] == "%"
