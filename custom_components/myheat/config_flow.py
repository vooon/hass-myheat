"""Adds config flow for MyHeat."""

import logging
from typing import Any

from homeassistant.config_entries import (
    CONN_CLASS_CLOUD_POLL,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import voluptuous as vol

from .api import MhApiClient
from .const import (
    CONF_API_KEY,
    CONF_DEVICE_ID,
    CONF_LOCAL_HOST,
    CONF_LOCAL_MODE_ENABLED,
    CONF_LOCAL_PASSWORD,
    CONF_LOCAL_POLL_INTERVAL,
    CONF_LOCAL_PROTOCOL,
    CONF_LOCAL_REQUEST_TIMEOUT,
    CONF_LOCAL_USERNAME,
    CONF_NAME,
    CONF_USERNAME,
    DEFAULT_LOCAL_POLL_INTERVAL,
    DEFAULT_LOCAL_PROTOCOL,
    DEFAULT_LOCAL_REQUEST_TIMEOUT,
    DOMAIN,
    LOCAL_PROTOCOLS,
)

_LOGGER = logging.getLogger(__package__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_DEVICE_ID): cv.positive_int,
    }
)


class MhFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for myheat."""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_CLOUD_POLL

    @staticmethod
    def async_get_options_flow(config_entry):
        """Create the options flow."""

        return MhOptionsFlowHandler(config_entry)

    @property
    def data_schema(self) -> vol.Schema:
        return DATA_SCHEMA

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""

        if user_input is None:
            return self._show_auth_config_form(user_input)

        self._devices = await self._get_devices(
            username=user_input[CONF_USERNAME],
            api_key=user_input[CONF_API_KEY],
        )
        if not self._devices:
            return self._show_auth_config_form(
                user_input, errors={"base": "invalid_auth"}
            )

        self._auth = user_input
        return await self.async_step_device()

    def _show_auth_config_form(
        self,
        user_input: dict[str, Any] | None = None,
        errors: dict[str, str] = {},
    ) -> ConfigFlowResult:  # pylint: disable=unused-argument
        """Show the configuration form to edit auth data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "api_key_url": "https://my.myheat.net",
            },
        )

    async def async_step_device(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show the configuration form to choose the device."""

        if not user_input:
            devices = [f"{v['id']} - {v['name']} - {v['city']}" for v in self._devices]

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
        unique_id = f"myheat{device_id}"

        user_input.update(self._auth)
        user_input[CONF_DEVICE_ID] = device_id

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

    async def _get_devices(self, username: str, api_key: str) -> list[Any]:
        """Return true if credentials is valid."""
        try:
            session = async_create_clientsession(self.hass)
            client = MhApiClient(
                username=username,
                api_key=api_key,
                device_id=None,
                session=session,
            )
            result = await client.async_get_devices()
            return result["devices"]
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("failed to get devices during config flow")
            pass
        return []


class MhOptionsFlowHandler(OptionsFlow):
    """Handle MyHeat options."""

    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Start the options flow."""

        return await self.async_step_local_init(user_input)

    async def async_step_local_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Manage local API options."""

        errors: dict[str, str] = {}
        if user_input is not None:
            if user_input.get(CONF_LOCAL_MODE_ENABLED):
                required = (
                    CONF_LOCAL_HOST,
                    CONF_LOCAL_USERNAME,
                    CONF_LOCAL_PASSWORD,
                )
                if any(not user_input.get(key) for key in required):
                    errors["base"] = "local_config_incomplete"
                else:
                    return self.async_create_entry(title="", data=user_input)
            else:
                return self.async_create_entry(title="", data=user_input)

        options = {
            CONF_LOCAL_MODE_ENABLED: False,
            CONF_LOCAL_PROTOCOL: DEFAULT_LOCAL_PROTOCOL,
            CONF_LOCAL_REQUEST_TIMEOUT: DEFAULT_LOCAL_REQUEST_TIMEOUT,
            CONF_LOCAL_POLL_INTERVAL: DEFAULT_LOCAL_POLL_INTERVAL,
            **self.config_entry.options,
        }

        return self.async_show_form(
            step_id="local_init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_LOCAL_MODE_ENABLED,
                        default=options.get(CONF_LOCAL_MODE_ENABLED, False),
                    ): bool,
                    vol.Optional(
                        CONF_LOCAL_HOST,
                        default=options.get(CONF_LOCAL_HOST, ""),
                    ): str,
                    vol.Required(
                        CONF_LOCAL_PROTOCOL,
                        default=options.get(
                            CONF_LOCAL_PROTOCOL,
                            DEFAULT_LOCAL_PROTOCOL,
                        ),
                    ): vol.In(LOCAL_PROTOCOLS),
                    vol.Optional(
                        CONF_LOCAL_USERNAME,
                        default=options.get(CONF_LOCAL_USERNAME, ""),
                    ): str,
                    vol.Optional(
                        CONF_LOCAL_PASSWORD,
                        default=options.get(CONF_LOCAL_PASSWORD, ""),
                    ): str,
                    vol.Required(
                        CONF_LOCAL_REQUEST_TIMEOUT,
                        default=options.get(
                            CONF_LOCAL_REQUEST_TIMEOUT,
                            DEFAULT_LOCAL_REQUEST_TIMEOUT,
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
                    vol.Required(
                        CONF_LOCAL_POLL_INTERVAL,
                        default=options.get(
                            CONF_LOCAL_POLL_INTERVAL,
                            DEFAULT_LOCAL_POLL_INTERVAL,
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
                }
            ),
            errors=errors,
        )
