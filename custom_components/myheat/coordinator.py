from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MhApiClient
from .const import DOMAIN  # noqa: F401

_LOGGER = logging.getLogger(__package__)

SCAN_INTERVAL = timedelta(seconds=30)

type MhConfigEntry = ConfigEntry[MhDataUpdateCoordinator]


class MhDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: MhConfigEntry,
        client: MhApiClient,
    ) -> None:
        """Initialize."""
        self.api = client

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=entry.title,
            update_interval=SCAN_INTERVAL,
            always_update=True,
        )

    async def _async_update_data(self) -> dict:
        """Update data via library."""
        try:
            return await self.api.async_get_device_info()
        except Exception as exception:
            raise UpdateFailed() from exception
