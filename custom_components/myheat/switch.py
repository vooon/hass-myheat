"""Switch platform for MyHeat."""

from itertools import chain

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import MhConfigEntry, MhDataUpdateCoordinator
from .entity import MhEntity, MhHeaterEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MhConfigEntry,
    async_add_devices: AddConfigEntryEntitiesCallback,
):
    """Setup sensor platform."""
    coordinator: MhDataUpdateCoordinator = entry.runtime_data
    async_add_devices(
        chain(
            (MhSecuritySwitch(coordinator, entry),),
            (
                MhHeaterEnabledSwitch(coordinator, entry, heater)
                for heater in coordinator.data.get("heaters", [])
                if heater.get("localControl", {}).get("enabled")
            ),
        )
    )


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


class MhHeaterEnabledSwitch(MhHeaterEntity, SwitchEntity):
    """Local heater enable switch."""

    _key = "enabled"
    _attr_icon = "mdi:electric-switch"

    @property
    def is_on(self) -> bool | None:
        heater = self.get_heater()
        if not heater:
            return None
        return not heater.get("disabled", False)

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        await self.coordinator.api.async_set_heater_enabled(
            obj_id=self.heater_id,
            enabled=True,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        await self.coordinator.api.async_set_heater_enabled(
            obj_id=self.heater_id,
            enabled=False,
        )
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self):
        """Write updated local heater state."""

        self.async_write_ha_state()
