"""Test MyHeat config flow."""

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry  # noqa: F401

from custom_components.myheat.const import BINARY_SENSOR  # noqa: F401
from custom_components.myheat.const import DOMAIN
from custom_components.myheat.const import PLATFORMS  # noqa: F401
from custom_components.myheat.const import SENSOR  # noqa: F401
from custom_components.myheat.const import SWITCH  # noqa: F401

from .const import MOCK_CONFIG, MOCK_DEVICE_CONFIG, MOCK_USER_CONFIG


# This fixture bypasses the actual setup of the integration
# since we only want to test the config flow. We test the
# actual functionality of the integration in other test modules.
@pytest.fixture(autouse=True)
def bypass_setup_fixture():
    """Prevent setup."""
    with (
        patch("custom_components.myheat.async_setup", return_value=True),
        patch("custom_components.myheat.async_setup_entry", return_value=True),
    ):
        yield


@pytest.mark.usefixtures(
    "mock_setup_entry",
    "bypass_get_devices",
)
async def test_successful_config_flow(hass):
    """Test a successful config flow."""
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    # If a user were to enter `test_username` for username and `test_password`
    # for password, it would result in this function call
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=MOCK_USER_CONFIG,
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "device"

    # If a user were to enter `test_username` for username and `test_password`
    # for password, it would result in this function call
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=MOCK_DEVICE_CONFIG,
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "test_device"
    assert result["data"] == MOCK_CONFIG
    assert result["result"]


@pytest.mark.usefixtures(
    "mock_setup_entry",
    "error_on_get_data",
)
async def test_failed_config_flow(hass):
    """Test a failed config flow due to credential validation failure."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=MOCK_USER_CONFIG,
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}
