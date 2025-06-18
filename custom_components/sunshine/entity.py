"""Base entity for Sunshine Scooter integration."""
from __future__ import annotations

from typing import Any

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunshineDataUpdateCoordinator


class SunshineEntity(CoordinatorEntity[SunshineDataUpdateCoordinator]):
    """Base class for Sunshine entities."""
    
    _attr_has_entity_name = True
    
    def __init__(self, coordinator: SunshineDataUpdateCoordinator, scooter_id: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.scooter_id = scooter_id
    
    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        scooter = self.coordinator.data.get(self.scooter_id, {})
        return {
            "identifiers": {(DOMAIN, self.scooter_id)},
            "name": f"Scooter {scooter.get('vin', self.scooter_id)}",
            "model": scooter.get("model", "Unknown"),
            "manufacturer": "Sunshine",
        }