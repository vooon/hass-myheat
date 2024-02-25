"""Sensor platform for MyHeat."""

from itertools import chain
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_NAME, DEFAULT_NAME, DOMAIN
from .entity import MhHeaterEntity, MhEntity

_logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    _logger.info(f"Setting up heater entries: {coordinator.data}")

    async_add_entities(
        chain.from_iterable(
            [
                MhHeaterFlowTempSensor(coordinator, entry, heater),
                MhHeaterReturnTempSensor(coordinator, entry, heater),
                MhHeaterTargetTempSensor(coordinator, entry, heater),
                MhHeaterPressureSensor(coordinator, entry, heater),
                MhHeaterModulationSensor(coordinator, entry, heater),
            ]
            for heater in coordinator.data.get("heaters", [])
        )
    )


class MhHeaterSensor(MhHeaterEntity, SensorEntity):
    """myheat Sensor class."""

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.get_heater().get(self._key)


class MhHeaterFlowTempSensor(MhHeaterSensor):
    _key = "flowTemp"
    _attr_icon = "mdi:coolant-temperature"
    _attr_device_class = "temperature"
    _attr_unit_of_measurement = UnitOfTemperature.CELSIUS


class MhHeaterReturnTempSensor(MhHeaterSensor):
    _key = "returnTemp"
    _attr_icon = "mdi:coolant-temperature"
    _attr_device_class = "temperature"
    _attr_unit_of_measurement = UnitOfTemperature.CELSIUS


class MhHeaterTargetTempSensor(MhHeaterSensor):
    _key = "targetTemp"
    _attr_icon = "mdi:coolant-temperature"
    _attr_device_class = "temperature"
    _attr_unit_of_measurement = UnitOfTemperature.CELSIUS


class MhHeaterPressureSensor(MhHeaterSensor):
    _key = "pressure"
    _attr_icon = "mdi:gauge"
    _attr_device_class = "pressure"


class MhHeaterModulationSensor(MhHeaterSensor):
    _key = "modulation"
    _attr_icon = "mdi:gas-burner"
    _attr_device_class = None
    _attr_unit_of_measurement = "%"
