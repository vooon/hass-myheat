"""Sensor platform for MyHeat."""

from itertools import chain

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import MhEntity, MhHeaterEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = chain(
        (MhWeatherTempSensor(coordinator, entry),),
        chain.from_iterable(
            [
                MhHeaterFlowTempSensor(coordinator, entry, heater),
                MhHeaterReturnTempSensor(coordinator, entry, heater),
                MhHeaterTargetTempSensor(coordinator, entry, heater),
                MhHeaterPressureSensor(coordinator, entry, heater),
                MhHeaterModulationSensor(coordinator, entry, heater),
            ]
            for heater in coordinator.data.get("heaters", [])
        ),
    )

    async_add_entities(entities)


class MhWeatherTempSensor(MhEntity, SensorEntity):
    """myheat weatherTemp Sensor class."""

    _attr_device_class = "temperature"
    _attr_unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def name(self) -> str:
        return f"{self._mh_name} weatherTemp"

    @property
    def unique_id(self):
        return f"{super().unique_id}weatherTemp"

    @property
    def state(self):
        return self.coordinator.data.get("weatherTemp")

    @property
    def extra_state_attributes(self):
        city = self.coordinator.data.get("city")
        return {
            "city": city,
        }


class MhHeaterSensor(MhHeaterEntity, SensorEntity):
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
