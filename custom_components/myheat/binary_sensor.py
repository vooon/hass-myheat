"""Binary sensor platform for MyHeat."""

from itertools import chain

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import MhConfigEntry, MhDataUpdateCoordinator
from .entity import MhEngEntity, MhEntity, MhEnvEntity, MhHeaterEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MhConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Setup sensor platform."""
    coordinator: MhDataUpdateCoordinator = entry.runtime_data

    entities = chain(
        (
            MhSeverityBinarySensor(coordinator, entry),
            MhDataActualBinarySensor(coordinator, entry),
            MhAlarmsBinarySensor(coordinator, entry),
        ),
        chain.from_iterable(
            [
                MhHeaterDisabledBinarySensor(coordinator, entry, heater),
                MhHeaterBurnerWaterBinarySensor(coordinator, entry, heater),
                MhHeaterBurnerHeatingBinarySensor(coordinator, entry, heater),
            ]
            for heater in coordinator.data.get("heaters", [])
        ),
        (
            MhEnvSeverityBinarySensor(coordinator, entry, env)
            for env in coordinator.data.get("envs", [])
        ),
        chain.from_iterable(
            [
                MhEngTurnedOnBinarySensor(coordinator, entry, eng),
                MhEngSeverityBinarySensor(coordinator, entry, eng),
            ]
            for eng in coordinator.data.get("engs", [])
        ),
    )

    async_add_entities(entities)


class MhDataActualBinarySensor(MhEntity, BinarySensorEntity):
    """myheat Data Actual (connected) Binary Sensor class."""

    _attr_device_class = "connectivity"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def name(self) -> str:
        return f"{self._mh_name} dataActual"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}dataActual"

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get("dataActual")


class MhAlarmsBinarySensor(MhEntity, BinarySensorEntity):
    """myheat Alarms Binary Sensor class."""

    _attr_device_class = "tamper"

    @property
    def name(self) -> str:
        return f"{self._mh_name} alarms"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}alarms"

    @property
    def is_on(self) -> bool | None:
        alarms = self.coordinator.data.get("alarms", [])
        return len(alarms) > 0

    @property
    def extra_state_attributes(self):
        alarms = self.coordinator.data.get("alarms", [])
        return {
            "alarms": alarms,
        }


class MhSeverityBinarySensorBase(BinarySensorEntity):
    _attr_device_class = "problem"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def _severity(self) -> (int | None, str | None):
        return None, None

    @property
    def is_on(self) -> bool | None:
        severity, _ = self._severity()
        if severity is None:
            return None

        # device_class:problem -> on means problem detected
        return severity != 1

    @property
    def extra_state_attributes(self) -> dict:
        severity, desc = self._severity()
        return {
            "value": severity,
            "description": desc,
        }


class MhSeverityBinarySensor(MhEntity, MhSeverityBinarySensorBase):
    _attr_icon = "mdi:water-boiler-alert"

    def _severity(self) -> (int | None, str | None):
        return (
            self.coordinator.data.get("severity"),
            self.coordinator.data.get("severityDesc"),
        )

    @property
    def name(self) -> str:
        return f"{self._mh_name} severity"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}severity"


class MhEnvSeverityBinarySensor(MhEnvEntity, MhSeverityBinarySensorBase):
    _key = "severity"
    _attr_icon = "mdi:water-boiler-alert"

    def _severity(self) -> (int | None, str | None):
        e = self.get_env()
        return (
            e.get("severity"),
            e.get("severityDesc"),
        )


class MhEngSeverityBinarySensor(MhEngEntity, MhSeverityBinarySensorBase):
    _key = "severity"

    def _severity(self) -> (int | None, str | None):
        e = self.get_eng()
        return (
            e.get("severity"),
            e.get("severityDesc"),
        )


class MhHeaterBinarySensor(MhHeaterEntity, BinarySensorEntity):
    @property
    def is_on(self) -> bool | None:
        return self.get_heater().get(self._key)


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


class MhEngTurnedOnBinarySensor(MhEngEntity, BinarySensorEntity):
    @property
    def is_on(self) -> bool | None:
        return self.get_eng().get("turnedOn")
