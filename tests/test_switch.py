"""Test MyHeat switch."""

from unittest.mock import call, patch

from homeassistant.components.switch import SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.const import ATTR_ENTITY_ID

from custom_components.myheat.const import SWITCH

from .helpers import setup_mock_entry


async def test_switch_services(hass, bypass_get_device_info):
    """Test switch services."""
    await setup_mock_entry(hass)

    entity_id = hass.states.async_entity_ids(SWITCH)[0]

    # Functions/objects can be patched directly in test code as well and can be used to test
    # additional things, like whether a function was called or what arguments it was called with
    with patch(
        "custom_components.myheat.MhApiClient.async_set_security_mode"
    ) as security_func:
        await hass.services.async_call(
            SWITCH,
            SERVICE_TURN_OFF,
            service_data={ATTR_ENTITY_ID: entity_id},
            blocking=True,
        )
        assert security_func.called
        assert security_func.call_args == call(mode=False)

        security_func.reset_mock()

        await hass.services.async_call(
            SWITCH,
            SERVICE_TURN_ON,
            service_data={ATTR_ENTITY_ID: entity_id},
            blocking=True,
        )
        assert security_func.called
        assert security_func.call_args == call(mode=True)
