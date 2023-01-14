"""Climate platform for MyHeat."""

from homeassistant.const import UnitOfTemperature
from homeassistant.components.climate import (
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_NONE,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)

from .const import CONF_NAME, DEFAULT_NAME, DOMAIN, ICON, Platform
from .entity import MhEntity
import logger

_logger = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup climate platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    await coordinator.async_request_refresh()

    for env in coordinator.data.get("data", {}).get("envs", []):
        async_add_devices([MhEnvClimate(coordinator, entry, env)])


class MhEnvClimate(MhEntity, ClimateEntity):
    """myheat Climate class."""

    def __init__(self, coordinator, config_entry, env):
        super().__init__(coordinator, config_entry)
        self.env = env

    @property
    def name(self):
        """Return the name of the sensor."""
        name = self.config_entry.data.get(CONF_NAME, DEFAULT_NAME)
        return f"{name} {self.env['name']}"

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._env().get("value")

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
