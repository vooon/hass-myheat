"""Water Heater platform for MyHeat."""

from typing import Any

from homeassistant.components.water_heater import (
    STATE_OFF,
    STATE_ON,
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api import WATER_HEATER_ENV_TYPES
from .coordinator import MhConfigEntry, MhDataUpdateCoordinator
from .entity import MhEnvEntity

DEFAULT_TURN_ON_GOAL = 45  # a sane DHW setpoint when no previous goal is known
OPERATION_MODE_ON = STATE_ON
OPERATION_MODE_OFF = STATE_OFF


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
            if env.get("type") in WATER_HEATER_ENV_TYPES
        ]
    )


class MhEnvWaterHeater(MhEnvEntity, WaterHeaterEntity):
    """myheat WaterHeater class."""

    _attr_target_temperature_high = 85.0
    _attr_target_temperature_low = 7.0
    _attr_target_temperature_step = 0.5
    _attr_max_temp = 85.0
    _attr_min_temp = 7.0
    # _attr_precision: float

    _attr_supported_features = (
        WaterHeaterEntityFeature.TARGET_TEMPERATURE
        | WaterHeaterEntityFeature.OPERATION_MODE
        | WaterHeaterEntityFeature.ON_OFF
    )

    _attr_operation_list = [
        OPERATION_MODE_OFF,
        OPERATION_MODE_ON,
    ]

    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        coordinator: MhDataUpdateCoordinator,
        config_entry: MhConfigEntry,
        env: dict,
    ):
        super().__init__(coordinator, config_entry, env)

        self._attr_current_temperature = None
        self._attr_target_temperature = None
        # Last goal seen while on: turning the heater back on restores it instead of sending 0.
        self._last_target: float | None = None

        self._update_state_attrs()

    async def _async_set_goal(self, goal: float | None) -> None:
        # changeMode=1 keeps the active regulation mode; changeMode=0 resets it.
        await self.coordinator.api.async_set_env_goal(
            obj_id=self.env_id, goal=goal, change_mode=goal is not None
        )
        await self.coordinator.async_request_refresh()

    def _goal_for_turn_on(self) -> float:
        if self._last_target:
            return self._last_target
        return DEFAULT_TURN_ON_GOAL

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the water heater on."""
        await self._async_set_goal(self._goal_for_turn_on())

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the water heater off."""
        await self._async_set_goal(None)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        await self._async_set_goal(kwargs.get("temperature", 0.0))

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set new target operation mode."""
        if operation_mode == OPERATION_MODE_OFF:
            await self._async_set_goal(None)
        elif operation_mode == OPERATION_MODE_ON:
            await self._async_set_goal(self._goal_for_turn_on())

    @property
    def extra_state_attributes(self) -> dict:
        e = self.get_env()
        return {
            "is_burning": e.get("demand", False),
        }

    def _update_state_attrs(self) -> None:
        """Update entity state attributes from coordinator data."""
        e = self.get_env()
        target = e.get("target")

        self._attr_current_temperature = e.get("value")
        # None while off: a 0.0 target would be re-sent as a real goal by turn_on.
        self._attr_target_temperature = target
        if target:
            self._last_target = target
        self._attr_current_operation = (
            OPERATION_MODE_ON if target is not None else OPERATION_MODE_OFF
        )

    @callback
    def _handle_coordinator_update(self):
        """Get the latest state from the thermostat."""
        self._update_state_attrs()
        self.async_write_ha_state()
