"""Test MyHeat setup process."""

from homeassistant.exceptions import ConfigEntryNotReady
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.myheat import (
    MhDataUpdateCoordinator,
    async_setup_entry,
)
from custom_components.myheat.const import DOMAIN

from .const import MOCK_CONFIG


async def test_async_setup_entry_default(hass, bypass_get_device_info):
    """Test entry setup and unload."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id) is True
    assert entry.runtime_data is not None and isinstance(
        entry.runtime_data, MhDataUpdateCoordinator
    )


async def test_setup_entry_exception(hass, error_on_get_data):
    """Test ConfigEntryNotReady when API raises an exception during entry setup."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    # In this case we are testing the condition where async_setup_entry raises
    # ConfigEntryNotReady using the `error_on_get_data` fixture which simulates
    # an error.
    with pytest.raises(ConfigEntryNotReady):
        assert await async_setup_entry(hass, config_entry)
