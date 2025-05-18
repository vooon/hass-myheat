import logging

from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse

from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_get_devices(call: ServiceCall) -> ServiceResponse:
    _LOGGER.error(f"get_devices called: {call}")
    return


async def async_get_device_info(call: ServiceCall) -> ServiceResponse:
    return


async def async_set_env_goal(call: ServiceCall) -> ServiceResponse:
    return


async def async_set_env_curve(call: ServiceCall) -> ServiceResponse:
    return


async def async_set_eng_goal(call: ServiceCall) -> ServiceResponse:
    return


async def async_set_heating_mode(call: ServiceCall) -> ServiceResponse:
    return


async def async_set_security_mode(call: ServiceCall) -> ServiceResponse:
    return


async def async_setup_services(hass: HomeAssistant):
    hass.services.async_register(DOMAIN, "get_devices", async_get_devices)
    hass.services.async_register(DOMAIN, "get_device_info", async_get_device_info)
    hass.services.async_register(DOMAIN, "set_env_goal", async_set_env_goal)
    hass.services.async_register(DOMAIN, "set_env_curve", async_set_env_curve)
    hass.services.async_register(DOMAIN, "set_eng_goal", async_set_eng_goal)
    hass.services.async_register(DOMAIN, "set_heating_mode", async_set_heating_mode)
    hass.services.async_register(DOMAIN, "set_security_mode", async_set_security_mode)
