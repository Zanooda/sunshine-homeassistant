"""Sensor platform for Sunshine Scooter integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SunshineDataUpdateCoordinator
from .entity import SunshineEntity

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: list[SensorEntityDescription] = [
    SensorEntityDescription(
        key="battery_level",
        name="Battery Level",
        native_unit_of_measurement="%",
        icon="mdi:battery",
    ),
    SensorEntityDescription(
        key="speed",
        name="Speed",
        native_unit_of_measurement="km/h",
        icon="mdi:speedometer",
    ),
    SensorEntityDescription(
        key="odometer",
        name="Odometer",
        native_unit_of_measurement="km",
        icon="mdi:counter",
    ),
    SensorEntityDescription(
        key="state",
        name="Status",
        icon="mdi:information-outline",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sunshine Scooter sensors."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    api = data["api"]
    coordinator = data["coordinator"]
    
    entities: list[SunshineSensor] = []
    
    for scooter_id in coordinator.data:
        for description in SENSOR_TYPES:
            entities.append(
                SunshineSensor(api, coordinator, scooter_id, description)
            )
    
    async_add_entities(entities)


class SunshineSensor(SunshineEntity, SensorEntity):
    """Representation of a Sunshine Scooter sensor."""
    
    def __init__(
        self,
        api,
        coordinator: SunshineDataUpdateCoordinator,
        scooter_id: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, scooter_id)
        self.api = api
        self.entity_description = description
        self._attr_unique_id = f"{scooter_id}_{description.key}"
    
    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if scooter_data := self.coordinator.data.get(self.scooter_id):
            if self.entity_description.key == "battery_level":
                if batteries := scooter_data.get("batteries"):
                    if battery0 := batteries.get("battery0"):
                        return battery0.get("level")
                return None

            value = scooter_data.get(self.entity_description.key)
            
            if value is None:
                return None
            
            if self.entity_description.key == "odometer":
                try:
                    return round(float(value) / 1000, 1)
                except (ValueError, TypeError):
                    _LOGGER.error("Invalid odometer value: %s", value)
                    return None
            
            return value
        return None