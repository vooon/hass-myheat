"""Test MyHeat setup process."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.myheat import MhDataUpdateCoordinator
from custom_components.myheat.const import DOMAIN

from .const import MOCK_CONFIG
from .helpers import setup_mock_entry


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
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id) is False
    assert entry.state is ConfigEntryState.SETUP_RETRY


async def test_child_devices_linked_via_device_id(hass, bypass_get_device_info, caplog):
    """Child devices must reference the controller device by via_device_id."""
    entry = await setup_mock_entry(hass)

    device_registry = dr.async_get(hass)
    controller = device_registry.async_get_device_by_identifier(
        (DOMAIN, entry.entry_id), entry.entry_id
    )
    assert controller is not None
    assert controller.via_device_id is None

    children = [
        device
        for device in dr.async_entries_for_config_entry(device_registry, entry.entry_id)
        if device.via_device_id == controller.id
    ]
    assert children
    for child in children:
        assert child.via_device_id != child.id

    assert "deprecated" not in caplog.text
