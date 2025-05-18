from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MhApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__package__)

SCAN_INTERVAL = timedelta(seconds=30)


class MhDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: MhApiClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
            config_entry=entry,
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.api.async_get_device_info()
        except Exception as exception:
            raise UpdateFailed() from exception
