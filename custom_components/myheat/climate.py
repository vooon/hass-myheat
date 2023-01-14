"""Climate platform for MyHeat."""

import logging

from homeassistant.components.climate import (
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_NONE,
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

        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

        self._attr_current_humidity = None
        self._attr_current_temperature = None

        self._attr_fan_mode = None
        self._attr_fan_modes = []

        self._attr_hvac_action = None
        self._attr_hvac_mode = HVACMode.AUTO
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]

        self._attr_is_aux_heat = False

        # self._attr_max_humidity = DEFAULT_MAX_HUMIDITY
        # self._attr_max_temp: float
        # self._attr_min_humidity: int = DEFAULT_MIN_HUMIDITY
        # self._attr_min_temp: float

        # self._attr_precision: float
        # self._attr_preset_mode: str | None
        # self._attr_preset_modes: list[str] | None

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
        return f"{self.config_entry.entry_id}env{self.env.get('id')}"

    # async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
    #     """Set new target hvac mode."""
    #     await self.hass.async_add_executor_job(self.set_hvac_mode, hvac_mode)

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""

        _logger.info(f"set t: {kwargs}")

    @callback
    def _handle_coordinator_update(self):
        """Get the latest state from the thermostat."""

        e = self._env()

        self._attr_current_temperature = e.get("value")
        self._attr_target_temperature = e.get("target")

        self._attr_hvac_action = (
            HVACAction.HEATING
            if self._attr_target_temperature is not None
            else HVACMode.OFF
        )

        self.async_write_ha_state()

    # @property
    # def device_class(self):
    #     """Return de device class of the sensor."""
    #     return "myheat__custom_device_class"

    def _env(self) -> dict:
        if not self.coordinator.data.get("data", {}).get("dataActual", False):
            _logger.warninig("data not actual! %s", self.coordinator.data)
            return {}

        envs = self.coordinator.data.get("data", {}).get("envs", [])
        for e in envs:
            if e["id"] == self.env["id"]:
                return e

        return {}
