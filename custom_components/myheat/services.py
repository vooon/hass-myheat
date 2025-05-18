import logging

from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.helpers import device_registry as dr

from .const import CONF_DEVICE_ID, DOMAIN
from .coordinator import MhDataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def _get_coordinator(call: ServiceCall) -> MhDataUpdateCoordinator:
    hass = call.hass
    device_id = call.data[CONF_DEVICE_ID][0]
    device_registry = dr.async_get(hass)

    if (device_entry := device_registry.async_get(device_id)) is None:
        raise ValueError(f"Invalid MyHeat device id: {device_id}")

    for entry_id in device_entry.config_entries:
        if (entry := hass.config_entries.async_get_entry(entry_id)) is None:
            continue
        if entry.domain == DOMAIN and entry.entry_id in hass.data[DOMAIN]:
            return hass.data[DOMAIN][entry.entry_id]

    raise ValueError(f"No controller for device id: {device_id}")


async def async_get_devices(call: ServiceCall) -> ServiceResponse:
    coordinator = await _get_coordinator(call)
    return await coordinator.api.async_get_devices()


async def async_get_device_info(call: ServiceCall) -> ServiceResponse:
    coordinator = await _get_coordinator(call)
    device_id = call.data.get("alt_device_id")
    return await coordinator.api.async_get_device_info(device_id=device_id)


async def async_set_env_goal(call: ServiceCall) -> ServiceResponse:
    coordinator = await _get_coordinator(call)
    device_id = call.data.get("alt_device_id")
    obj_id = call.data["obj_id"]
    goal = call.data["goal"]
    change_mode = call.data.get("change_mode", False)
    return await coordinator.api.async_set_env_goal(
        device_id=device_id,
        obj_id=obj_id,
        goal=goal,
        change_mode=change_mode,
    )


async def async_set_env_curve(call: ServiceCall) -> ServiceResponse:
    coordinator = await _get_coordinator(call)
    device_id = call.data.get("alt_device_id")
    obj_id = call.data["obj_id"]
    curve = call.data["curve"]
    change_mode = call.data.get("change_mode", False)
    return await coordinator.api.async_set_env_curve(
        device_id=device_id,
        obj_id=obj_id,
        curve=curve,
        change_mode=change_mode,
    )


async def async_set_eng_goal(call: ServiceCall) -> ServiceResponse:
    coordinator = await _get_coordinator(call)
    device_id = call.data.get("alt_device_id")
    obj_id = call.data["obj_id"]
    goal = call.data["goal"]
    change_mode = call.data.get("change_mode", False)
    return await coordinator.api.async_set_eng_goal(
        device_id=device_id,
        obj_id=obj_id,
        goal=goal,
        change_mode=change_mode,
    )


async def async_set_heating_mode(call: ServiceCall) -> ServiceResponse:
    coordinator = await _get_coordinator(call)
    device_id = call.data.get("alt_device_id")
    mode_id = call.data.get("mode_id")
    schedule_id = call.data.get("schedule_id")
    return await coordinator.api.async_set_heating_mode(
        device_id=device_id,
        mode_id=mode_id,
        schedule_id=schedule_id,
    )


async def async_set_security_mode(call: ServiceCall) -> ServiceResponse:
    coordinator = await _get_coordinator(call)
    device_id = call.data.get("alt_device_id")
    mode = call.data["mode"]
    return await coordinator.api.async_set_security_mode(
        device_id=device_id,
        mode=mode,
    )


async def async_refresh(call: ServiceCall) -> ServiceResponse:
    coordinator = await _get_coordinator(call)
    return await coordinator.async_refresh()


async def async_setup_services(hass: HomeAssistant):
    hass.services.async_register(
        DOMAIN,
        "get_devices",
        async_get_devices,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        "get_device_info",
        async_get_device_info,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(DOMAIN, "set_env_goal", async_set_env_goal)
    hass.services.async_register(DOMAIN, "set_env_curve", async_set_env_curve)
    hass.services.async_register(DOMAIN, "set_eng_goal", async_set_eng_goal)
    hass.services.async_register(DOMAIN, "set_heating_mode", async_set_heating_mode)
    hass.services.async_register(DOMAIN, "set_security_mode", async_set_security_mode)
    hass.services.async_register(DOMAIN, "refresh", async_refresh)
