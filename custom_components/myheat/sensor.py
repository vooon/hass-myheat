"""Sensor platform for MyHeat."""

from itertools import chain

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfPressure,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api import (
    CLIMATE_ENV_TYPES,
    ENV_TYPE_HUMIDITY,
    PRESSURE_ENV_TYPES,
    TEMPERATURE_ENV_TYPES,
    WATER_HEATER_ENV_TYPES,
)
from .coordinator import MhConfigEntry, MhDataUpdateCoordinator
from .entity import MhEntity, MhEnvEntity, MhHeaterEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MhConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Setup sensor platform."""
    coordinator: MhDataUpdateCoordinator = entry.runtime_data

    entities = chain(
        (MhWeatherTempSensor(coordinator, entry),),
        (
            sensor
            for sensor in (
                MhLocalGsmRssiSensor(coordinator, entry),
                MhLocalGsmBalanceSensor(coordinator, entry),
            )
            if sensor.available
        ),
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
        (
            MhEnvSensor(coordinator, entry, env)
            for env in coordinator.data.get("envs", [])
            if env.get("type") not in CLIMATE_ENV_TYPES | WATER_HEATER_ENV_TYPES
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


class MhEnvSensor(MhEnvEntity, SensorEntity):
    """Sensor for environment values that cannot be controlled.

    Env types that are neither climate nor water heater entities (humidity,
    outdoor temperature, and any unknown numeric zone value) are exposed as
    plain sensors instead of falling back to a water heater.
    """

    def __init__(
        self,
        coordinator: MhDataUpdateCoordinator,
        config_entry: MhConfigEntry,
        env: dict,
    ):
        super().__init__(coordinator, config_entry, env)

        env_type = env.get("type")
        if env_type == ENV_TYPE_HUMIDITY:
            self._attr_device_class = SensorDeviceClass.HUMIDITY
            self._attr_native_unit_of_measurement = PERCENTAGE
        elif env_type in TEMPERATURE_ENV_TYPES:
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif env_type in PRESSURE_ENV_TYPES:
            self._attr_device_class = SensorDeviceClass.PRESSURE
            self._attr_native_unit_of_measurement = UnitOfPressure.BAR

    @property
    def native_value(self) -> float | None:
        return self.get_env().get("value")


class MhLocalSensor(MhEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _local_key: str

    @property
    def available(self) -> bool:
        return self.native_value is not None

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.get("local", {}).get(self._local_key)
        return float(value) if value is not None else None


class MhLocalGsmRssiSensor(MhLocalSensor):
    _local_key = "gsmRssi"
    _attr_icon = "mdi:signal-cellular-2"
    _attr_native_unit_of_measurement = PERCENTAGE

    @property
    def name(self) -> str:
        return f"{self._mh_name} GSM RSSI"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}gsmRssi"


class MhLocalGsmBalanceSensor(MhLocalSensor):
    _local_key = "gsmBalance"
    _attr_icon = "mdi:sim"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "RUB"

    @property
    def name(self) -> str:
        return f"{self._mh_name} GSM balance"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}gsmBalance"


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
