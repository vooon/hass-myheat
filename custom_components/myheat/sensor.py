"""Sensor platform for MyHeat."""

from itertools import chain
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_NAME, DEFAULT_NAME, DOMAIN
from .entity import MhEntity

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


class MhHeaterSensor(MhEntity, SensorEntity):
    """myheat Sensor class."""

    _key = ""

    def __init__(self, coordinator, config_entry, heater: dict):
        super().__init__(coordinator, config_entry)
        self.heater_name = heater["name"]
        self.heater_id = heater["id"]

    @property
    def name(self):
        """Return the name of the sensor."""
        name = self.config_entry.data.get(CONF_NAME, DEFAULT_NAME)
        return f"{name} {self.heater_name} {self._key}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._heater().get(self._key)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{super().unique_id}htr{self.heater_id}{self._key}"

    @property
    def device_info(self) -> dict:
        d = super().device_info
        d["name"] += f" Heater {self.heater_name}"
        return d

    def _heater(self) -> dict:
        heaters = self.coordinator.data.get("heaters", [])
        for h in heaters:
            if h["id"] == self.heater_id:
                return h
        return {}


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
