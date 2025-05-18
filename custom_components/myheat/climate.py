"""Climate platform for MyHeat."""

from homeassistant.components.climate import (
    PRESET_AWAY,
    PRESET_ECO,
    PRESET_HOME,
    PRESET_NONE,
    PRESET_SLEEP,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.components.climate import PRESET_ACTIVITY  # noqa: F401
from homeassistant.components.climate import PRESET_BOOST  # noqa: F401
from homeassistant.components.climate import PRESET_COMFORT  # noqa: F401
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import MhConfigEntry, MhDataUpdateCoordinator
from .entity import MhEnvEntity

PRESET_TO_ID = {
    # PRESET_ACTIVITY: 0,
    PRESET_AWAY: 3,  # Режим: Отпуск
    # PRESET_BOOST: 0,
    # PRESET_COMFORT: 0,
    PRESET_ECO: 2,  # Режим: На работе
    PRESET_HOME: 1,  # Режим: Дома
    PRESET_NONE: 0,
    PRESET_SLEEP: 4,  # Режим: Лето
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MhConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Setup climate platform."""
    coordinator: MhDataUpdateCoordinator = entry.runtime_data

    async_add_entities(
        [
            MhEnvClimate(coordinator, entry, env)
            for env in coordinator.data.get("envs", [])
        ]
    )


class MhEnvClimate(MhEnvEntity, ClimateEntity):
    """myheat Climate class."""

    def __init__(
        self,
        coordinator: MhDataUpdateCoordinator,
        config_entry: MhConfigEntry,
        env: dict,
    ):
        super().__init__(coordinator, config_entry, env)

        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
        )

        self._attr_current_humidity = None
        self._attr_current_temperature = None

        self._attr_fan_mode = None
        self._attr_fan_modes = []

        self._attr_hvac_action = None
        self._attr_hvac_mode = HVACMode.OFF
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]

        self._attr_is_aux_heat = False

        # self._attr_max_humidity = DEFAULT_MAX_HUMIDITY
        # self._attr_max_temp: float
        # self._attr_min_humidity: int = DEFAULT_MIN_HUMIDITY
        # self._attr_min_temp: float

        # self._attr_precision: float
        self._attr_preset_mode = PRESET_NONE
        self._attr_preset_modes = list(PRESET_TO_ID.keys())

        # self._attr_swing_mode: str | None
        # self._attr_swing_modes: list[str] | None

        # self._attr_target_humidity = None
        # self._attr_target_temperature_high = None
        # self._attr_target_temperature_low = None
        self._attr_target_temperature_step = 1.0
        self._attr_target_temperature = None

        self._attr_temperature_unit = UnitOfTemperature.CELSIUS

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""

        if hvac_mode == HVACMode.OFF:
            goal = None
        else:
            goal = self._attr_target_temperature
            if goal is None:
                goal = 24  # NOTE(vooon): we need some reasonable value to turn on the heater and i like 22-26.

        await self.coordinator.api.async_set_env_goal(obj_id=self.env_id, goal=goal)
        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        mode_id = PRESET_TO_ID[preset_mode]
        await self.coordinator.api.async_set_heating_mode(mode_id=mode_id)
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        goal = kwargs.get("temperature", 0.0)
        await self.coordinator.api.async_set_env_goal(obj_id=self.env_id, goal=goal)
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self):
        """Get the latest state from the thermostat."""

        e = self.get_env()

        self._attr_current_temperature = e.get("value")
        self._attr_target_temperature = e.get("target")

        self._attr_hvac_action = (
            (HVACAction.HEATING if e.get("demand", False) else HVACAction.IDLE)
            if self._attr_target_temperature is not None
            else HVACAction.OFF
        )

        self._attr_hvac_mode = (
            HVACMode.HEAT if self._attr_target_temperature is not None else HVACMode.OFF
        )

        self.async_write_ha_state()
