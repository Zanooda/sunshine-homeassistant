"""Switch platform for Sunshine Scooter integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SunshineDataUpdateCoordinator
from .entity import SunshineEntity

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


class SunshineLockSwitch(SunshineEntity, SwitchEntity):
    """Representation of a Sunshine Scooter lock switch."""
    
    def __init__(self, api, coordinator: SunshineDataUpdateCoordinator, scooter_id: str) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, scooter_id)
        self.api = api
        self._attr_unique_id = f"{scooter_id}_lock"
        self._attr_icon = "mdi:lock"
        self._attr_name = "Lock"
    
    @property
    def is_on(self) -> bool:
        """Return true if the scooter is locked."""
        if scooter_data := self.coordinator.data.get(self.scooter_id):
            state = scooter_data.get("state")
            if state:
                # Following the logic from the Rails model: unlocked if state is 'parked' or 'ready-to-drive'
                return state not in ["parked", "ready-to-drive"]
        return True  # Default to locked if no data
    
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Lock the scooter."""
        try:
            await self.api.lock(self.scooter_id)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to lock scooter %s: %s", self.scooter_id, err)
    
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Unlock the scooter."""
        try:
            await self.api.unlock(self.scooter_id)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to unlock scooter %s: %s", self.scooter_id, err)