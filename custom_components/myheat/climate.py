"""Climate platform for MyHeat."""

from .const import DEFAULT_NAME
from .const import DOMAIN
from .const import ICON
from .const import Platform
from .entity import MhEntity

from homeassistant.components.climate import (
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_NONE,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup climate platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([MhClimate(coordinator, entry)])


class MhClimate(MhEntity, ClimateEntity):
    """myheat Climate class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_{Platform.CLIMATE}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("body")

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

    @property
    def device_class(self):
        """Return de device class of the sensor."""
        return "myheat__custom_device_class"
