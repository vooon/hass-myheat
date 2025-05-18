"""MhEntity class"""

import logging

from homeassistant.headers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CONF_DEVICE_ID,
    CONF_NAME,
    DEFAULT_NAME,
    DOMAIN,
    MANUFACTURER,
    VERSION,
)
from .coordinator import MhConfigEntry, MhDataUpdateCoordinator

_logger = logging.getLogger(__package__)


class MhEntity(CoordinatorEntity[MhDataUpdateCoordinator]):
    def __init__(
        self,
        coordinator: MhDataUpdateCoordinator,
        config_entry: MhConfigEntry,
    ):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def unique_id(self) -> str:
        return self.config_entry.entry_id

    @property
    def device_info(self) -> DeviceInfo:
        name = self.config_entry.data.get(CONF_NAME, DEFAULT_NAME)
        name += self._mh_dev_name_suffix
        info = DeviceInfo(
            identifiers={self._mh_identifiers},
            name=name,
            model=VERSION,
            manufacturer=MANUFACTURER,
        )
        if self._mh_identifiers != self._mh_via_device:
            info.via_device = self._mh_via_device
        return info

    @property
    def _mh_dev_name_suffix(self) -> str:
        return ""

    @property
    def _mh_identifiers(self) -> tuple[str, str]:
        return (DOMAIN, self.config_entry.entry_id)

    @property
    def _mh_via_device(self) -> tuple[str, str]:
        return (DOMAIN, self.config_entry.entry_id)

    @property
    def _mh_name(self) -> str:
        return self.config_entry.data.get(CONF_NAME, DEFAULT_NAME)

    @property
    def device_state_attributes(self) -> dict:
        return {
            "attribution": ATTRIBUTION,
            "id": str(self.config_entry.data.get(CONF_DEVICE_ID)),
            "integration": DOMAIN,
        }


class MhHeaterEntity(MhEntity):
    """Heater element"""

    _key: str | None = None
    heater_name: str = ""
    heater_id: int = 0

    def __init__(
        self,
        coordinator: MhDataUpdateCoordinator,
        config_entry: MhConfigEntry,
        heater: dict,
    ):
        super().__init__(coordinator, config_entry)
        self.heater_name = heater["name"]
        self.heater_id = heater["id"]

    @property
    def name(self) -> str:
        return (
            f"{self._mh_name} {self.heater_name}{' ' + self._key if self._key else ''}"
        )

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}htr{self.heater_id}{self._key if self._key else ''}"

    @property
    def _mh_dev_name_suffix(self) -> str:
        return f" {self.heater_name}"

    @property
    def _mh_identifiers(self) -> tuple[str, str]:
        return (DOMAIN, f"{super().unique_id}htr{self.heater_id}")

    def get_heater(self) -> dict:
        """Return heater state data"""
        if not self.coordinator.data.get("dataActual", False):
            _logger.warninig("data not actual! %s", self.coordinator.data)
            return {}

        for h in self.coordinator.data.get("heaters", []):
            if h["id"] == self.heater_id:
                return h

        return {}


class MhEnvEntity(MhEntity):
    """Env element"""

    _key: str | None = None
    env_name: str = ""
    env_id: int = 0

    def __init__(
        self,
        coordinator: MhDataUpdateCoordinator,
        config_entry: MhConfigEntry,
        env: dict,
    ):
        super().__init__(coordinator, config_entry)
        self.env_name = env["name"]
        self.env_id = env["id"]

    @property
    def name(self) -> str:
        return f"{self._mh_name} {self.env_name}{' ' + self._key if self._key else ''}"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}env{self.env_id}{self._key if self._key else ''}"

    @property
    def _mh_dev_name_suffix(self) -> str:
        return f" {self.env_name}"

    @property
    def _mh_identifiers(self) -> tuple[str, str]:
        return (DOMAIN, f"{super().unique_id}env{self.env_id}")

    def get_env(self) -> dict:
        """Return env state data"""
        if not self.coordinator.data.get("dataActual", False):
            _logger.warninig("data not actual! %s", self.coordinator.data)
            return {}

        for e in self.coordinator.data.get("envs", []):
            if e["id"] == self.env_id:
                return e

        return {}


class MhEngEntity(MhEntity):
    """Eng element"""

    _key: str | None = None
    eng_name: str = ""
    eng_id: int = 0

    def __init__(
        self,
        coordinator: MhDataUpdateCoordinator,
        config_entry: MhConfigEntry,
        eng: dict,
    ):
        super().__init__(coordinator, config_entry)
        self.eng_name = eng["name"]
        self.eng_id = eng["id"]

    @property
    def name(self) -> str:
        return f"{self._mh_name} {self.eng_name}{' ' + self._key if self._key else ''}"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}eng{self.eng_id}{self._key if self._key else ''}"

    @property
    def _mh_dev_name_suffix(self) -> str:
        return f" {self.eng_name}"

    @property
    def _mh_identifiers(self) -> tuple[str, str]:
        return (DOMAIN, f"{super().unique_id}eng{self.eng_id}")

    def get_eng(self) -> dict:
        """Return eng state data"""
        if not self.coordinator.data.get("dataActual", False):
            _logger.warninig("data not actual! %s", self.coordinator.data)
            return {}

        for e in self.coordinator.data.get("engs", []):
            if e["id"] == self.eng_id:
                return e

        return {}
