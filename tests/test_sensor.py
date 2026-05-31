"""Test MyHeat sensors."""

from copy import deepcopy
from unittest.mock import patch

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import UnitOfPressure, UnitOfTemperature

from .const import MOCK_GET_DEVICE_INFO
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

    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 13

    rssi = state_by_name(hass, SENSOR_DOMAIN, "test_device GSM RSSI")
    assert rssi.state == "74.0"
    assert rssi.attributes["unit_of_measurement"] == "%"

    balance = state_by_name(hass, SENSOR_DOMAIN, "test_device GSM balance")
    assert balance.state == "137.7"
    assert balance.attributes["device_class"] == SensorDeviceClass.MONETARY
    assert balance.attributes["unit_of_measurement"] == "RUB"
