"""
Custom integration to integrate MyHeat with Home Assistant.

For more details about this integration, please refer to
https://github.com/vooon/hass-myheat
"""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .api import MhApiClient
from .const import (
    CONF_API_KEY,
    CONF_DEVICE_ID,
    CONF_NAME,
    CONF_USERNAME,
    DEFAULT_NAME,
    DOMAIN,
    MANUFACTURER,
    PLATFORMS,
    STARTUP_MESSAGE,
    VERSION,
)
from .coordinator import MhConfigEntry, MhDataUpdateCoordinator
from .services import async_setup_services

_LOGGER: logging.Logger = logging.getLogger(__package__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up this integration using YAML is not supported."""
    await async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: MhConfigEntry):
    """Set up this integration using UI."""
    if DOMAIN not in hass.data:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    username = entry.data.get(CONF_USERNAME)
    api_key = entry.data.get(CONF_API_KEY)
    device_id = entry.data.get(CONF_DEVICE_ID)

    session = async_get_clientsession(hass)
    client = MhApiClient(
        username=username,
        api_key=api_key,
        device_id=device_id,
        session=session,
    )

    coordinator = MhDataUpdateCoordinator(hass, client=client, entry=entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        manufacturer=MANUFACTURER,
        model=VERSION,
        name=entry.data.get(CONF_NAME, DEFAULT_NAME),
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.add_update_listener(async_reload_entry)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: MhConfigEntry) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: MhConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
