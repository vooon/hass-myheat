"""Climate platform for MyHeat."""

import logging

from homeassistant.components.climate import (
    PRESET_ACTIVITY,
    PRESET_AWAY,
    PRESET_BOOST,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_HOME,
    PRESET_NONE,
    PRESET_SLEEP,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_NAME, DEFAULT_NAME, DOMAIN
from .entity import MhEntity

_logger = logging.getLogger(__package__)

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
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup climate platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    _logger.info(f"Setting up env entries: {coordinator.data}")

    async_add_entities(
        [
            MhEnvClimate(coordinator, entry, env)
            for env in coordinator.data.get("data", {}).get("envs", [])
        ]
    )


class MhEnvClimate(MhEntity, ClimateEntity):
    """myheat Climate class."""

    def __init__(self, coordinator, config_entry, env):
        super().__init__(coordinator, config_entry)
        self.env = env

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
        self._attr_preset_modes = PRESET_TO_ID.keys()

        # self._attr_swing_mode: str | None
        # self._attr_swing_modes: list[str] | None

        # self._attr_target_humidity = None
        # self._attr_target_temperature_high = None
        # self._attr_target_temperature_low = None
        self._attr_target_temperature_step = 1.0
        self._attr_target_temperature = None

        self._attr_temperature_unit = UnitOfTemperature.CELSIUS

    @property
    def name(self):
        """Return the name of the sensor."""
        name = self.config_entry.data.get(CONF_NAME, DEFAULT_NAME)
        return f"{name} {self.env['name']}"

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{super().unique_id}env{self.env.get('id')}"

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""

        if hvac_mode == HVACMode.OFF:
            goal = None
        else:
            goal = self._attr_target_temperature
            if goal is None:
                goal = 24  # NOTE(vooon): we need some reasonable value to turn on the heater and i like 22-26.

        await self.coordinator.api.async_set_env_goal(obj_id=self.env["id"], goal=goal)
        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        mode_id = PRESET_TO_ID[preset_mode]
        await self.coordinator.api.async_set_heating_mode(mode_id=mode_id)
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        goal = kwargs.get("temperature", 0)
        await self.coordinator.api.async_set_env_goal(obj_id=self.env["id"], goal=goal)
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self):
        """Get the latest state from the thermostat."""

        e = self._env()

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

    @property
    def device_info(self) -> dict:
        d = super().device_info
        d["name"] += f" Env {self.env['name']}"
        return d

    def _env(self) -> dict:
        if not self.coordinator.data.get("data", {}).get("dataActual", False):
            _logger.warninig("data not actual! %s", self.coordinator.data)
            return {}

        envs = self.coordinator.data.get("data", {}).get("envs", [])
        for e in envs:
            if e["id"] == self.env["id"]:
                return e

        return {}
