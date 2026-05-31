"""Helpers for MyHeat tests."""

from homeassistant.const import ATTR_FRIENDLY_NAME
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.myheat.const import DOMAIN

from .const import MOCK_CONFIG


async def setup_mock_entry(hass) -> MockConfigEntry:
    """Set up the integration with a mock config entry."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id) is True
    await hass.async_block_till_done()
    return entry


def state_by_name(hass, domain: str, friendly_name: str):
    """Return an entity state by its friendly name."""
    available_names = []
    for state in hass.states.async_all(domain):
        name = state.attributes.get(ATTR_FRIENDLY_NAME)
        available_names.append(name)
        if name == friendly_name:
            return state

    raise AssertionError(
        f"State not found: {domain}.{friendly_name}; available: {available_names}"
    )
