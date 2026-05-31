"""Test MyHeat binary sensors."""

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.const import STATE_OFF, STATE_ON

from .helpers import setup_mock_entry, state_by_name


async def test_binary_sensor_entities(hass, bypass_get_device_info):
    """Test binary sensor entities are created from coordinator data."""
    await setup_mock_entry(hass)

    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 23

    data_actual = state_by_name(hass, BINARY_SENSOR_DOMAIN, "test_device dataActual")
    assert data_actual.state == STATE_ON

    alarms = state_by_name(hass, BINARY_SENSOR_DOMAIN, "test_device Alarms")
    assert alarms.state == STATE_OFF
    assert alarms.attributes["alarms"] == {}

    severity = state_by_name(hass, BINARY_SENSOR_DOMAIN, "test_device Severity")
    assert severity.state == STATE_OFF
    assert severity.attributes["value"] == 1
    assert severity.attributes["description"] == "Система работает нормально."

    heater_disabled = state_by_name(
        hass, BINARY_SENSOR_DOMAIN, "test_device Vaillant правый Disabled"
    )
    assert heater_disabled.state == STATE_OFF

    eng_state = state_by_name(hass, BINARY_SENSOR_DOMAIN, "test_device Насос магазин")
    assert eng_state.state == STATE_OFF
