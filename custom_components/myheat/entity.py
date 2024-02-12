"""MhEntity class"""

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CONF_DEVICE_ID,
    CONF_NAME,
    DEFAULT_NAME,
    DOMAIN,
    MANUFACTURER,
    NAME,
    VERSION,
)


class MhEntity(CoordinatorEntity):
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id

    @property
    def device_info(self) -> dict:
        name = self.config_entry.data.get(CONF_NAME, DEFAULT_NAME)
        info = {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": name,
            "model": VERSION,
            "manufacturer": MANUFACTURER,
        }
        if self.unique_id != self.config_entry.entry_id:
            info["via_device"] = self._mh_via_device
        return info

    @property
    def _mh_via_device(self):
        """Return a unique ID to use for this entity."""
        return (DOMAIN, self.config_entry.entry_id)

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": str(self.config_entry.data.get(CONF_DEVICE_ID)),
            "integration": DOMAIN,
        }
