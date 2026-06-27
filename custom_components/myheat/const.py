"""Constants for MyHeat."""

from homeassistant.const import CONF_API_KEY  # noqa: F401
from homeassistant.const import CONF_DEVICE_ID  # noqa: F401
from homeassistant.const import CONF_NAME  # noqa: F401
from homeassistant.const import CONF_USERNAME  # noqa: F401
from homeassistant.const import Platform

# Base component constants
NAME = "MyHeat.net"
DOMAIN = "myheat"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.9.2"

ATTRIBUTION = "https://myheat.net"
MANUFACTURER = "https://myheat.net"

ISSUE_URL = "https://github.com/vooon/hass-myheat/issues"


# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
SWITCH = "switch"

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.WATER_HEATER,
]

# Defaults
DEFAULT_NAME = DOMAIN
DEFAULT_CLOUD_POLL_INTERVAL = 30
DEFAULT_LOCAL_POLL_INTERVAL = 10
DEFAULT_LOCAL_PROTOCOL = "http"
DEFAULT_LOCAL_REQUEST_TIMEOUT = 15

LOCAL_SENTINEL = -16777216

CONF_LOCAL_MODE_ENABLED = "local_mode_enabled"
CONF_LOCAL_HOST = "local_host"
CONF_LOCAL_PASSWORD = "local_password"
CONF_LOCAL_POLL_INTERVAL = "local_poll_interval"
CONF_LOCAL_PROTOCOL = "local_protocol"
CONF_LOCAL_REQUEST_TIMEOUT = "local_request_timeout"
CONF_LOCAL_USERNAME = "local_username"

LOCAL_PROTOCOLS = ["http", "https"]


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
