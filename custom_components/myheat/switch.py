"""Switch platform for MyHeat."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import MhEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback,
):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([MhSecuritySwitch(coordinator, entry)])


class MhSecuritySwitch(MhEntity, SwitchEntity):
    """myheat switch class."""

    _attr_icon = "mdi:security"

    @property
    def name(self) -> str:
        return f"{self._mh_name} security alarm"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}security"

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        await self.coordinator.api.async_set_security_mode(mode=True)
        # NOTE: we cannot query the state, so we have to make some assumptions
        self._attr_is_on = True

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        await self.coordinator.api.async_set_security_mode(mode=False)
        self._attr_is_on = False
