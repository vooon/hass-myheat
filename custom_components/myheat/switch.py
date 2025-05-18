"""Switch platform for MyHeat."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import MhConfigEntry, MhDataUpdateCoordinator
from .entity import MhEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MhConfigEntry,
    async_add_devices: AddConfigEntryEntitiesCallback,
):
    """Setup sensor platform."""
    coordinator: MhDataUpdateCoordinator = entry.runtime_data
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
