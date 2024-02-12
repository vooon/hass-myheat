"""Binary sensor platform for MyHeat."""

from itertools import flatten
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
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
        flatten(
            [
                MhHeaterDisabledBinarySensor(coordinator, entry, heater),
                MhHeaterBurnerWaterBinarySensor(coordinator, entry, heater),
                MhHeaterBurnerHeatingBinarySensor(coordinator, entry, heater),
            ]
            for heater in coordinator.data.get("heaters", [])
        )
    )


class MhHeaterBinarySensor(MhEntity, BinarySensorEntity):
    """myheat Binary Sensor class."""

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
    def is_on(self):
        """Return true if the binary_sensor is on."""
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


class MhHeaterDisabledBinarySensor(MhHeaterBinarySensor):
    _attr_name = "disabled"
    _icon = "mdi:electric-switch"
    _attr_device_class = None


class MhHeaterBurnerWaterBinarySensor(MhHeaterBinarySensor):
    _attr_name = "burnerWater"
    _icon = "mdi:fire"
    _attr_device_class = "heat"


class MhHeaterBurnerHeatingBinarySensor(MhHeaterBinarySensor):
    _attr_name = "burnerHeating"
    _icon = "mdi:fire"
    _attr_device_class = "heat"
