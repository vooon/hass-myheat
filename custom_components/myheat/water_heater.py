"""Water Heater platform for MyHeat."""

from typing import Any

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api import ENV_TYPE_ROOM_TEMPERATURE
from .coordinator import MhConfigEntry, MhDataUpdateCoordinator
from .entity import MhEnvEntity

OPERATION_MODE_ON = "on"
OPERATION_MODE_OFF = "off"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MhConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Setup water_heater platform."""
    coordinator: MhDataUpdateCoordinator = entry.runtime_data

    async_add_entities(
        [
            MhEnvWaterHeater(coordinator, entry, env)
            for env in coordinator.data.get("envs", [])
            if env.get("type") not in [ENV_TYPE_ROOM_TEMPERATURE]
        ]
    )


class MhEnvWaterHeater(MhEnvEntity, WaterHeaterEntity):
    """myheat WaterHeater class."""

    def __init__(
        self,
        coordinator: MhDataUpdateCoordinator,
        config_entry: MhConfigEntry,
        env: dict,
    ):
        super().__init__(coordinator, config_entry, env)

        self._attr_supported_features = (
            WaterHeaterEntityFeature.TARGET_TEMPERATURE
            | WaterHeaterEntityFeature.ON_OFF
        )

        self._attr_current_temperature = None

        # self._attr_max_temp: float
        # self._attr_min_temp: float

        # self._attr_precision: float

        # self._attr_target_temperature_high = None
        # self._attr_target_temperature_low = None
        self._attr_target_temperature_step = 1.0
        self._attr_target_temperature = None

        self._attr_temperature_unit = UnitOfTemperature.CELSIUS

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the water heater on."""
        goal = self._attr_target_temperature
        await self.coordinator.api.async_set_env_goal(obj_id=self.env_id, goal=goal)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the water heater off."""
        goal = None
        await self.coordinator.api.async_set_env_goal(obj_id=self.env_id, goal=goal)
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        goal = kwargs.get("temperature", 0.0)
        await self.coordinator.api.async_set_env_goal(obj_id=self.env_id, goal=goal)
        await self.coordinator.async_request_refresh()

    @property
    def extra_state_attributes(self) -> dict:
        e = self.get_env()
        return {
            "is_burning": e.get("demand", False),
        }

    @callback
    def _handle_coordinator_update(self):
        """Get the latest state from the thermostat."""

        e = self.get_env()

        self._attr_current_temperature = e.get("value")
        self._attr_target_temperature = e.get("target")
        self._attr_current_operation = (
            OPERATION_MODE_ON if e.get("target") is not None else OPERATION_MODE_OFF
        )

        self.async_write_ha_state()
