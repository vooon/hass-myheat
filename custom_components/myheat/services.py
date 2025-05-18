import logging

from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse

from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_get_devices(call: ServiceCall) -> ServiceResponse:
    _LOGGER.error(f"get_devices called: {call}")
    return


async def async_setup_services(hass: HomeAssistant):
    hass.services.async_register(DOMAIN, "get_devices", async_get_devices)
