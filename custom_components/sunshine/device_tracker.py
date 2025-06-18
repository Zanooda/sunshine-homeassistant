"""Device tracker platform for Sunshine Scooter integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.device_tracker import TrackerEntity
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
    """Set up Sunshine Scooter device tracker."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    api = data["api"]
    coordinator = data["coordinator"]
    
    entities: list[SunshineDeviceTracker] = []
    
    for scooter_id in coordinator.data:
        entities.append(SunshineDeviceTracker(api, coordinator, scooter_id))
    
    async_add_entities(entities)


class SunshineDeviceTracker(CoordinatorEntity[SunshineDataUpdateCoordinator], TrackerEntity):
    """Representation of a Sunshine Scooter device tracker."""
    
    def __init__(
        self,
        api,
        coordinator: SunshineDataUpdateCoordinator,
        scooter_id: str,
    ) -> None:
        """Initialize the device tracker."""
        super().__init__(coordinator)
        self.api = api
        self.scooter_id = scooter_id
        
        self._attr_unique_id = f"{scooter_id}_tracker"
        self._attr_icon = "mdi:scooter"
    
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
        """Return the name of the device tracker."""
        scooter = self.coordinator.data[self.scooter_id]
        return f"{scooter.get('vin', self.scooter_id)} Location"
    
    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        return self.coordinator.data[self.scooter_id].get("latitude")
    
    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        return self.coordinator.data[self.scooter_id].get("longitude")
    
    @property
    def battery_level(self) -> int | None:
        """Return the battery level of the device."""
        return self.coordinator.data[self.scooter_id].get("battery_level")
    
    @property
    def location_accuracy(self) -> int:
        """Return the location accuracy of the device."""
        # Return a default accuracy of 10 meters if not provided by API
        return self.coordinator.data[self.scooter_id].get("location_accuracy", 10)
    
    @property
    def source_type(self) -> str:
        """Return the source type, eg gps or router, of the device."""
        return "gps"