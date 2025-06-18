"""Switch platform for Sunshine Scooter integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunshineDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sunshine Scooter switches."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    api = data["api"]
    coordinator = data["coordinator"]
    
    entities: list[SunshineLockSwitch] = []
    
    for scooter_id in coordinator.data:
        entities.append(SunshineLockSwitch(api, coordinator, scooter_id))
    
    async_add_entities(entities)


class SunshineLockSwitch(CoordinatorEntity[SunshineDataUpdateCoordinator], SwitchEntity):
    """Representation of a Sunshine Scooter lock switch."""
    
    def __init__(self, api, coordinator: SunshineDataUpdateCoordinator, scooter_id: str) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.api = api
        self.scooter_id = scooter_id
        
        self._attr_unique_id = f"{scooter_id}_lock"
        self._attr_icon = "mdi:lock"
    
    @property
    def device_info(self) -> dict[str, Any]:
        """Return device info."""
        scooter = self.coordinator.data[self.scooter_id]
        return {
            "identifiers": {(DOMAIN, self.scooter_id)},
            "name": f"Scooter {scooter.get('vin', self.scooter_id)}",
            "model": scooter.get("model", "Unknown"),
            "manufacturer": "Sunshine",
        }
    
    @property
    def name(self) -> str:
        """Return the name of the switch."""
        scooter = self.coordinator.data[self.scooter_id]
        return f"{scooter.get('vin', self.scooter_id)} Lock"
    
    @property
    def is_on(self) -> bool:
        """Return true if the scooter is locked."""
        return self.coordinator.data[self.scooter_id].get("locked", True)
    
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Lock the scooter."""
        try:
            await self.api.lock(self.scooter_id)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to lock scooter %s: %s", self.scooter_id, err)
            raise
    
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Unlock the scooter."""
        try:
            await self.api.unlock(self.scooter_id)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to unlock scooter %s: %s", self.scooter_id, err)
            raise