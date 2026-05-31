"""Sensor platform for MyHeat."""

from itertools import chain

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import PERCENTAGE, UnitOfPressure, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import MhConfigEntry, MhDataUpdateCoordinator
from .entity import MhEntity, MhHeaterEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MhConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Setup sensor platform."""
    coordinator: MhDataUpdateCoordinator = entry.runtime_data

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

    _attr_icon = "mdi:weather-cloudy"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def name(self) -> str:
        return f"{self._mh_name} weatherTemp"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}weatherTemp"

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.get("weatherTemp")
        return float(value) if value is not None else None

    @property
    def extra_state_attributes(self) -> dict:
        city = self.coordinator.data.get("city")
        return {
            "city": city,
        }


class MhHeaterSensor(MhHeaterEntity, SensorEntity):
    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.get_heater().get(self._key)


class MhHeaterFlowTempSensor(MhHeaterSensor):
    _key = "flowTemp"
    _attr_icon = "mdi:coolant-temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS


class MhHeaterReturnTempSensor(MhHeaterSensor):
    _key = "returnTemp"
    _attr_icon = "mdi:coolant-temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS


class MhHeaterTargetTempSensor(MhHeaterSensor):
    _key = "targetTemp"
    _attr_icon = "mdi:coolant-temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS


class MhHeaterPressureSensor(MhHeaterSensor):
    _key = "pressure"
    _attr_icon = "mdi:gauge"
    _attr_device_class = SensorDeviceClass.PRESSURE
    _attr_native_unit_of_measurement = UnitOfPressure.BAR


class MhHeaterModulationSensor(MhHeaterSensor):
    _key = "modulation"
    _attr_icon = "mdi:gas-burner"
    _attr_device_class = None
    _attr_native_unit_of_measurement = PERCENTAGE
