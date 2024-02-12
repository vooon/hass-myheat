"""Binary sensor platform for MyHeat."""

from itertools import chain
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
        [
            MhSeverityBinarySensor(coordinator, entry),
        ]
        + list(
            chain.from_iterable(
                [
                    MhHeaterDisabledBinarySensor(coordinator, entry, heater),
                    MhHeaterBurnerWaterBinarySensor(coordinator, entry, heater),
                    MhHeaterBurnerHeatingBinarySensor(coordinator, entry, heater),
                ]
                for heater in coordinator.data.get("heaters", [])
            )
        )
        + list(
            MhEngBinarySensor(coordinator, entry, eng)
            for eng in coordinator.data.get("engs", [])
        )
    )


class MhHeaterBinarySensor(MhEntity, BinarySensorEntity):
    """myheat Binary Sensor class."""

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
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{super().unique_id}htr{self.heater_id}{self._key}"

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self._heater().get(self._key)

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
    _key = "disabled"
    _attr_icon = "mdi:electric-switch"
    _attr_device_class = None


class MhHeaterBurnerWaterBinarySensor(MhHeaterBinarySensor):
    _key = "burnerWater"
    _attr_icon = "mdi:fire"
    _attr_device_class = "heat"


class MhHeaterBurnerHeatingBinarySensor(MhHeaterBinarySensor):
    _key = "burnerHeating"
    _attr_icon = "mdi:fire"
    _attr_device_class = "heat"


class MhSeverityBinarySensor(MhEntity, BinarySensorEntity):
    """myheat Binary Sensor class."""

    _attr_device_class = "problem"
    _attr_icon = "mdi:water-boiler-alert"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        name = self.config_entry.data.get(CONF_NAME, DEFAULT_NAME)
        return f"{name} severity"

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{super().unique_id}severity"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary_sensor is on."""

        severity = self.coordinator.data.get("severity")
        if severity is None:
            return None

        return severity > 1

    def extra_state_attributes(self):
        desc = self.coordinator.data.get("severityDesc")
        return {
            "description": desc,
        }


class MhEngBinarySensor(MhEntity, BinarySensorEntity):
    """myheat Binary Sensor class."""

    def __init__(self, coordinator, config_entry, eng: dict):
        super().__init__(coordinator, config_entry)
        self.eng_name = eng["name"]
        self.eng_id = eng["id"]

    @property
    def name(self):
        """Return the name of the sensor."""
        name = self.config_entry.data.get(CONF_NAME, DEFAULT_NAME)
        return f"{name} {self.eng_name}"

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{super().unique_id}eng{self.eng_id}"

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self._eng().get("turnedOn")

    @property
    def device_info(self) -> dict:
        d = super().device_info
        d["name"] += f" Eng {self.eng_name}"
        return d

    def _eng(self) -> dict:
        engs = self.coordinator.data.get("engs", [])
        for e in engs:
            if e["id"] == self.eng_id:
                return e
        return {}
