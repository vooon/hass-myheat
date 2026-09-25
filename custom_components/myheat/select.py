"""Select platform for MyHeat engineering components."""

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api import ENG_GOAL_AUTO, ENG_GOAL_OFF, ENG_GOAL_ON
from .coordinator import MhConfigEntry, MhDataUpdateCoordinator
from .entity import MhEngEntity

OPTION_AUTO = "auto"
OPTION_ON = "on"
OPTION_OFF = "off"

OPTIONS = [OPTION_AUTO, OPTION_ON, OPTION_OFF]

GOAL_BY_OPTION = {
    OPTION_AUTO: ENG_GOAL_AUTO,
    OPTION_ON: ENG_GOAL_ON,
    OPTION_OFF: ENG_GOAL_OFF,
}

OPTION_BY_GOAL = {
    ENG_GOAL_AUTO: OPTION_AUTO,
    ENG_GOAL_ON: OPTION_ON,
    ENG_GOAL_OFF: OPTION_OFF,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MhConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Setup select platform."""
    coordinator: MhDataUpdateCoordinator = entry.runtime_data

    async_add_entities(
        MhEngSelect(coordinator, entry, eng) for eng in coordinator.data.get("engs", [])
    )


class MhEngSelect(MhEngEntity, SelectEntity):
    """Control mode for a MyHeat engineering component.

    MyHeat exposes a single three-state goal for pumps, actuators and valves:
    automatic regulation, forced on, or forced off.
    """

    _key = "Mode"
    _attr_icon = "mdi:tune-variant"
    _attr_options = OPTIONS

    @property
    def current_option(self) -> str | None:
        goal = self.get_eng().get("mode")
        if goal is None:
            return OPTION_AUTO

        try:
            goal = int(goal)
        except TypeError, ValueError:
            return OPTION_AUTO

        # Any negative goal (including the local sentinel) means automatic.
        if goal < 0:
            return OPTION_AUTO
        return OPTION_BY_GOAL.get(goal, OPTION_AUTO)

    async def async_select_option(self, option: str) -> None:
        """Set the engineering component goal."""
        await self.coordinator.api.async_set_eng_goal(
            obj_id=self.eng_id,
            goal=GOAL_BY_OPTION[option],
        )
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Write updated engineering component state."""
        self.async_write_ha_state()
