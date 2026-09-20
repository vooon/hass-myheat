"""Test MyHeat sensors."""

from copy import deepcopy
from unittest.mock import patch

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.water_heater import DOMAIN as WATER_HEATER_DOMAIN
from homeassistant.const import PERCENTAGE, UnitOfPressure, UnitOfTemperature

from .const import MOCK_GET_DEVICE_INFO
from .helpers import setup_mock_entry, state_by_name


async def test_sensor_entities(hass, bypass_get_device_info):
    """Test sensor entities are created from coordinator data."""
    await setup_mock_entry(hass)

    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 12

    weather = state_by_name(hass, SENSOR_DOMAIN, "test_device weatherTemp")
    assert weather.state == "-6.78999999999996"
    assert weather.attributes["city"] == "Новошешминск"
    assert weather.attributes["unit_of_measurement"] == UnitOfTemperature.CELSIUS

    humidity = state_by_name(hass, SENSOR_DOMAIN, "test_device Влажность")
    assert humidity.state == "45.5"
    assert humidity.attributes["device_class"] == SensorDeviceClass.HUMIDITY
    assert humidity.attributes["unit_of_measurement"] == PERCENTAGE

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


async def test_other_env_types_become_sensors(hass):
    """Test non-controllable env types fall back to sensors, not water heaters."""
    data = deepcopy(MOCK_GET_DEVICE_INFO["data"])
    data["envs"].extend(
        [
            {
                "id": 91,
                "type": "outdoor_temperature",
                "name": "Уличная температура",
                "value": 19,
                "target": None,
                "demand": False,
                "severity": 1,
                "severityDesc": "Нормальное состояние.",
            },
            {
                "id": 92,
                "type": "some_unknown_value",
                "name": "Что-то",
                "value": 3.5,
                "target": None,
                "demand": False,
                "severity": 1,
                "severityDesc": "Нормальное состояние.",
            },
        ]
    )

    with patch(
        "custom_components.myheat.MhApiClient.async_get_device_info",
        return_value=data,
    ):
        await setup_mock_entry(hass)

    assert len(hass.states.async_entity_ids(WATER_HEATER_DOMAIN)) == 2

    outdoor = state_by_name(hass, SENSOR_DOMAIN, "test_device Уличная температура")
    assert outdoor.state == "19"
    assert outdoor.attributes["device_class"] == SensorDeviceClass.TEMPERATURE
    assert outdoor.attributes["unit_of_measurement"] == UnitOfTemperature.CELSIUS

    unknown = state_by_name(hass, SENSOR_DOMAIN, "test_device Что-то")
    assert unknown.state == "3.5"
    assert unknown.attributes.get("unit_of_measurement") is None
    assert unknown.attributes.get("device_class") is None


async def test_local_gsm_sensor_entities(hass):
    """Test local GSM diagnostic sensors."""
    data = deepcopy(MOCK_GET_DEVICE_INFO["data"])
    data["local"] = {
        "gsmRssi": 74,
        "gsmBalance": 137.7,
    }

    with patch(
        "custom_components.myheat.MhApiClient.async_get_device_info",
        return_value=data,
    ):
        await setup_mock_entry(hass)

    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 14

    rssi = state_by_name(hass, SENSOR_DOMAIN, "test_device GSM RSSI")
    assert rssi.state == "74.0"
    assert rssi.attributes["unit_of_measurement"] == "%"

    balance = state_by_name(hass, SENSOR_DOMAIN, "test_device GSM balance")
    assert balance.state == "137.7"
    assert balance.attributes["device_class"] == SensorDeviceClass.MONETARY
    assert balance.attributes["unit_of_measurement"] == "RUB"
