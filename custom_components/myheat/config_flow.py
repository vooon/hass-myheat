"""Adds config flow for MyHeat."""

import logging

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import voluptuous as vol

from .api import MhApiClient
from .const import CONF_API_KEY, CONF_DEVICE_ID, CONF_NAME, CONF_USERNAME, DOMAIN

_logger = logging.getLogger(__name__)


class MhFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for myheat."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._devices = {}
        self._errors = {}

    @property
    def data_schema(self):
        return vol.Schema(
            {
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_DEVICE_ID): int,
            }
        )

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is None:
            return await self._show_auth_config_form(user_input)

        self._devices = await self._get_devices(
            user_input[CONF_USERNAME], user_input[CONF_API_KEY]
        )
        if not self._devices:
            self._errors["base"] = "auth"
            return await self._show_auth_config_form(user_input)

        return await self.async_step_device(user_input)

    async def _show_auth_config_form(
        self, user_input
    ):  # pylint: disable=unused-argument
        """Show the configuration form to edit auth data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=self._errors,
        )

    async def async_step_device(self, user_input=None):
        """Show the configuration form to choose the device."""
        if not user_input:
            devices = [
                f"{v[id]} - {v[name]} - {v[city]}"
                for v in self._devices["data"]["devices"]
            ]

            return self.async_show_form(
                step_id="device",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_NAME): str,
                        vol.Required(CONF_DEVICE_ID): vol.In(devices),
                    }
                ),
            )

        device_id = int(user_input[CONF_DEVICE_ID].strip().split(" ")[0])
        unique_id = f"myheat-{device_id}"

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

    async def _get_devices(self, username, api_key):
        """Return true if credentials is valid."""
        try:
            session = async_create_clientsession(self.hass)
            client = MhApiClient(username, api_key, None, session)
            return await client.async_get_devices()
        except Exception:  # pylint: disable=broad-except
            pass
        return {}
