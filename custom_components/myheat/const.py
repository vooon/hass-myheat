"""Constants for MyHeat."""
from homeassistant.const import CONF_API_KEY
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.const import CONF_NAME
from homeassistant.const import CONF_USERNAME
from homeassistant.const import Platform

# Base component constants
NAME = "MyHeat"
DOMAIN = "myheat"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.1.0"

ATTRIBUTION = "https://myheat.net"
MANUFACTURER = "https://myheat.net"

ISSUE_URL = "https://github.com/vooon/hass-myheat/issues"

# Icons
ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
SWITCH = "switch"

PLATFORMS = [Platform.CLIMATE]

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
