"""Test MyHeat binary sensors."""

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.const import STATE_OFF, STATE_ON

from .helpers import setup_mock_entry, state_by_name


async def test_binary_sensor_entities(hass, bypass_get_device_info):
    """Test binary sensor entities are created from coordinator data."""
    await setup_mock_entry(hass)

    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 34

    data_actual = state_by_name(hass, BINARY_SENSOR_DOMAIN, "test_device dataActual")
    assert data_actual.state == STATE_ON

    alarms = state_by_name(hass, BINARY_SENSOR_DOMAIN, "test_device Alarms")
    assert alarms.state == STATE_OFF
    assert alarms.attributes["alarms"] == [
        {
            "id": 301,
            "type": "water_leakage",
            "name": "Протечка воды",
            "alarm": False,
            "severity": 1,
            "severityDesc": "Нормальное состояние.",
        },
        {
            "id": 1778385145,
            "type": "water_leakage",
            "name": "Протечка воды Котельная",
            "alarm": False,
            "severity": 1,
            "severityDesc": "Нормальное состояние.",
        },
    ]

    water_leakage = state_by_name(
        hass, BINARY_SENSOR_DOMAIN, "test_device Протечка воды"
    )
    assert water_leakage.state == STATE_OFF
    assert water_leakage.attributes["type"] == "water_leakage"
    assert water_leakage.attributes["severity"] == 1
    assert water_leakage.attributes["description"] == "Нормальное состояние."

    boiler_room_leakage = state_by_name(
        hass, BINARY_SENSOR_DOMAIN, "test_device Протечка воды Котельная"
    )
    assert boiler_room_leakage.state == STATE_OFF
    assert boiler_room_leakage.attributes["type"] == "water_leakage"
    assert boiler_room_leakage.attributes["severity"] == 1

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

    active_eng_state = state_by_name(
        hass, BINARY_SENSOR_DOMAIN, "test_device Насос ГВС рециркуляции"
    )
    assert active_eng_state.state == STATE_ON

    valve_state = state_by_name(
        hass, BINARY_SENSOR_DOMAIN, "test_device Сервопривод 2этаж ТП Ванная"
    )
    assert valve_state.state == STATE_OFF

    eng_severity = state_by_name(
        hass,
        BINARY_SENSOR_DOMAIN,
        "test_device Клапан 3-ходовой Баня/Конвекторы Severity",
    )
    assert eng_severity.state == STATE_OFF
    assert eng_severity.attributes["value"] == 1
    assert eng_severity.attributes["description"] == "Режим регулирования."
