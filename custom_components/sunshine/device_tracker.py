"""Device tracker platform for Sunshine Scooter integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.device_tracker import TrackerEntity
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
    """Set up Sunshine Scooter device tracker."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    api = data["api"]
    coordinator = data["coordinator"]
    
    entities: list[SunshineDeviceTracker] = []
    
    for scooter_id in coordinator.data:
        entities.append(SunshineDeviceTracker(api, coordinator, scooter_id))
    
    async_add_entities(entities)


class SunshineDeviceTracker(SunshineEntity, TrackerEntity):
    """Representation of a Sunshine Scooter device tracker."""
    
    def __init__(
        self,
        api,
        coordinator: SunshineDataUpdateCoordinator,
        scooter_id: str,
    ) -> None:
        """Initialize the device tracker."""
        super().__init__(coordinator, scooter_id)
        self.api = api
        self._attr_unique_id = f"{scooter_id}_tracker"
        self._attr_icon = "mdi:scooter"
        self._attr_name = "Location"
    
    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        if scooter_data := self.coordinator.data.get(self.scooter_id):
            if location := scooter_data.get("location"):
                try:
                    lat_val = location.get("lat")
                    if lat_val is not None:
                        return float(lat_val)
                except (ValueError, TypeError):
                    _LOGGER.warning("Invalid latitude value for scooter %s: %s", self.scooter_id, location.get("lat"))
        return None
    
    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        if scooter_data := self.coordinator.data.get(self.scooter_id):
            if location := scooter_data.get("location"):
                try:
                    lng_val = location.get("lng")
                    if lng_val is not None:
                        return float(lng_val)
                except (ValueError, TypeError):
                    _LOGGER.warning("Invalid longitude value for scooter %s: %s", self.scooter_id, location.get("lng"))
        return None
    
    @property
    def battery_level(self) -> int | None:
        """Return the battery level of the device."""
        if scooter_data := self.coordinator.data.get(self.scooter_id):
            if batteries := scooter_data.get("batteries"):
                if battery0 := batteries.get("battery0"):
                    if (level := battery0.get("level")) is not None:
                        try:
                            return int(level)
                        except (ValueError, TypeError):
                            _LOGGER.warning("Invalid battery level for scooter %s: %s", self.scooter_id, level)
        return None
    
    @property
    def location_accuracy(self) -> int:
        """Return the location accuracy of the device."""
        # Return a default accuracy of 10 meters if not provided by API
        if scooter_data := self.coordinator.data.get(self.scooter_id):
            return scooter_data.get("location_accuracy", 10)
        return 10
    
    @property
    def source_type(self) -> str:
        """Return the source type, eg gps or router, of the device."""
        return "gps"