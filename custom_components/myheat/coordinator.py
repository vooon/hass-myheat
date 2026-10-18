from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (  # noqa: F401
    DEFAULT_CLOUD_POLL_INTERVAL,
    DEFAULT_UPDATE_FAILURE_TOLERANCE,
    DOMAIN,
)

_LOGGER = logging.getLogger(__package__)

SCAN_INTERVAL = timedelta(seconds=DEFAULT_CLOUD_POLL_INTERVAL)

type MhConfigEntry = ConfigEntry[MhDataUpdateCoordinator]


class MhDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: MhConfigEntry,
        client: Any,
        scan_interval: timedelta = SCAN_INTERVAL,
        failure_tolerance: int = DEFAULT_UPDATE_FAILURE_TOLERANCE,
    ) -> None:
        """Initialize."""
        self.api = client
        self._failure_tolerance = failure_tolerance
        self._consecutive_failures = 0

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=entry.title,
            update_interval=scan_interval,
            always_update=True,
        )

    async def _async_update_data(self) -> dict:
        """Update data via library."""
        try:
            data = await self.api.async_get_device_info()
        except Exception as exception:
            self._consecutive_failures += 1
            # Keep serving the last good data for a few polls so a flaky link
            # (e.g. LTE) does not flip every entity to unavailable on each miss.
            if (
                self.data is not None
                and self._consecutive_failures <= self._failure_tolerance
            ):
                _LOGGER.warning(
                    "%s: update failed (%d/%d tolerated), keeping previous data: %r",
                    self.name,
                    self._consecutive_failures,
                    self._failure_tolerance,
                    exception,
                )
                return self.data
            raise UpdateFailed() from exception

        self._consecutive_failures = 0
        return data
