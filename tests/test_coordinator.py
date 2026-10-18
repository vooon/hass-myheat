"""Test MyHeat data update coordinator."""

from unittest.mock import patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.myheat.const import (
    CONF_CLOUD_REQUEST_TIMEOUT,
    CONF_UPDATE_FAILURE_TOLERANCE,
    DEFAULT_CLOUD_REQUEST_TIMEOUT,
    DOMAIN,
)

from .const import MOCK_CONFIG, MOCK_GET_DEVICE_INFO

# Patch the hybrid client, not the cloud one: it caches cloud data for the cloud
# poll interval, so a failing cloud call would not be reached on every refresh.
GET_DEVICE_INFO = (
    "custom_components.myheat.hybrid_api.MhHybridApiClient.async_get_device_info"
)


async def _setup_entry(hass, options: dict | None = None) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG, options=options or {}, entry_id="test"
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id) is True
    await hass.async_block_till_done()
    return entry


async def test_default_options(hass, bypass_get_device_info):
    """Defaults apply when the entry has no cloud options."""
    entry = await _setup_entry(hass)
    coordinator = entry.runtime_data

    assert coordinator.api.cloud._request_timeout == DEFAULT_CLOUD_REQUEST_TIMEOUT
    assert coordinator._failure_tolerance == 0


async def test_options_applied(hass, bypass_get_device_info):
    """Cloud options are passed to the API client and the coordinator."""
    entry = await _setup_entry(
        hass,
        {CONF_CLOUD_REQUEST_TIMEOUT: 45, CONF_UPDATE_FAILURE_TOLERANCE: 2},
    )
    coordinator = entry.runtime_data

    assert coordinator.api.cloud._request_timeout == 45
    assert coordinator._failure_tolerance == 2


async def test_failure_without_tolerance(hass, bypass_get_device_info):
    """With the default tolerance the first failed update marks data stale."""
    entry = await _setup_entry(hass)
    coordinator = entry.runtime_data

    with patch(GET_DEVICE_INFO, side_effect=TimeoutError):
        await coordinator.async_refresh()

    assert coordinator.last_update_success is False


async def test_failure_tolerance(hass, bypass_get_device_info, caplog):
    """Previous data is kept for the tolerated number of consecutive failures."""
    entry = await _setup_entry(hass, {CONF_UPDATE_FAILURE_TOLERANCE: 2})
    coordinator = entry.runtime_data
    previous = coordinator.data

    with patch(GET_DEVICE_INFO, side_effect=TimeoutError):
        for attempt in (1, 2):
            await coordinator.async_refresh()
            assert coordinator.last_update_success is True
            assert coordinator.data is previous
            assert f"update failed ({attempt}/2 tolerated)" in caplog.text

        await coordinator.async_refresh()
        assert coordinator.last_update_success is False

    await coordinator.async_refresh()
    assert coordinator.last_update_success is True
    assert coordinator._consecutive_failures == 0

    # The counter restarts after a success, so the next failure is tolerated again.
    with patch(GET_DEVICE_INFO, side_effect=TimeoutError):
        await coordinator.async_refresh()
    assert coordinator.last_update_success is True
    assert coordinator.data == MOCK_GET_DEVICE_INFO["data"]
