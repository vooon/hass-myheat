"""Sensor platform for MyHeat."""

from itertools import flatten
import logging

from homeassistant.components.sensor import SensorEntity

from .const import CONF_NAME, DEFAULT_NAME, DOMAIN
from .entity import MhEntity

_logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    _logger.info(f"Setting up env entries: {coordinator.data}")

    async_add_entities(
        flatten(
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

    _attr_name = ""
    _icon = "mdi:water-boiler"

    def __init__(self, coordinator, config_entry, heater: dict):
        super().__init__(coordinator, config_entry)
        self.heater_name = heater["name"]
        self.heater_id = heater["id"]

    @property
    def name(self):
        """Return the name of the sensor."""
        name = self.config_entry.data.get(CONF_NAME, DEFAULT_NAME)
        return f"{name} {self.heater_name} {self._attr_name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._heater().get(self._attr_name)

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

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
    _attr_name = "flowTemp"
    _icon = "mdi:coolant-temperature"
    _attr_device_class = "temperature"


class MhHeaterReturnTempSensor(MhHeaterSensor):
    _attr_name = "returnTemp"
    _icon = "mdi:coolant-temperature"
    _attr_device_class = "temperature"


class MhHeaterTargetTempSensor(MhHeaterSensor):
    _attr_name = "targetTemp"
    _icon = "mdi:coolant-temperature"
    _attr_device_class = "temperature"


class MhHeaterPressureSensor(MhHeaterSensor):
    _attr_name = "pressure"
    _icon = "mdi:gauge"
    _attr_device_class = "pressure"


class MhHeaterModulationSensor(MhHeaterSensor):
    _attr_name = "modulation"
    _icon = "mdi:gas-burner"
    _attr_device_class = None
