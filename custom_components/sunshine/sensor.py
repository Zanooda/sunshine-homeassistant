"""Sensor platform for Sunshine Scooter integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunshineDataUpdateCoordinator

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
        key="status",
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


class SunshineSensor(CoordinatorEntity[SunshineDataUpdateCoordinator], SensorEntity):
    """Representation of a Sunshine Scooter sensor."""
    
    def __init__(
        self,
        api,
        coordinator: SunshineDataUpdateCoordinator,
        scooter_id: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.api = api
        self.scooter_id = scooter_id
        self.entity_description = description
        
        self._attr_unique_id = f"{scooter_id}_{description.key}"
    
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
        """Return the name of the sensor."""
        scooter = self.coordinator.data[self.scooter_id]
        return f"{scooter.get('vin', self.scooter_id)} {self.entity_description.name}"
    
    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        return self.coordinator.data[self.scooter_id].get(self.entity_description.key)