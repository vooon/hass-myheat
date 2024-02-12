"""Global fixtures for MyHeat integration."""

from unittest.mock import patch

import pytest

from .const import MOCK_GET_DEVICE_INFO


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with patch("homeassistant.components.persistent_notification.async_create"), patch(
        "homeassistant.components.persistent_notification.async_dismiss"
    ):
        yield


@pytest.fixture
def bypass_get_device_info():
    """Skip calls to get data from API."""
    with patch(
        "custom_components.myheat.MhApiClient.async_get_device_info",
        return_value=MOCK_GET_DEVIDE_INFO["data"],
    ):
        yield


@pytest.fixture
def bypass_get_devices():
    """Skip calls to get data from API."""
    with patch(
        "custom_components.myheat.MhApiClient.async_get_devices",
        return_value=MOCK_GET_DEVIDE_INFO["data"],
    ):
        yield


@pytest.fixture(name="error_on_get_data")
def error_get_data_fixture():
    """Simulate error when retrieving data from API."""
    with patch(
        "custom_components.myheat.MhApiClient.rpc",
        side_effect=Exception,
    ):
        yield
