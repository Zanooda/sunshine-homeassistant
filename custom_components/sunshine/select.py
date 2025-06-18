"""Select platform for Sunshine Scooter integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    BLINKER_BOTH,
    BLINKER_LEFT,
    BLINKER_OFF,
    BLINKER_RIGHT,
    DOMAIN,
    SOUND_ALARM,
    SOUND_CHIRP,
    SOUND_FIND_ME,
)
from .coordinator import SunshineDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class SunshineSelectEntityDescription(SelectEntityDescription):
    """Describes Sunshine select entity."""
    
    api_method: str | None = None
    api_param_key: str | None = None


SELECT_TYPES: list[SunshineSelectEntityDescription] = [
    SunshineSelectEntityDescription(
        key="blinkers",
        name="Blinkers",
        icon="mdi:car-light-high",
        options=[BLINKER_OFF, BLINKER_LEFT, BLINKER_RIGHT, BLINKER_BOTH],
        api_method="blinkers",
        api_param_key="state",
    ),
    SunshineSelectEntityDescription(
        key="sound",
        name="Play Sound",
        icon="mdi:volume-high",
        options=[SOUND_ALARM, SOUND_CHIRP, SOUND_FIND_ME],
        api_method="play_sound",
        api_param_key="sound",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sunshine Scooter select entities."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    api = data["api"]
    coordinator = data["coordinator"]
    
    entities: list[SunshineSelect] = []
    
    for scooter_id in coordinator.data:
        for description in SELECT_TYPES:
            entities.append(
                SunshineSelect(api, coordinator, scooter_id, description)
            )
    
    async_add_entities(entities)


class SunshineSelect(CoordinatorEntity[SunshineDataUpdateCoordinator], SelectEntity):
    """Representation of a Sunshine Scooter select entity."""
    
    entity_description: SunshineSelectEntityDescription
    
    def __init__(
        self,
        api,
        coordinator: SunshineDataUpdateCoordinator,
        scooter_id: str,
        description: SunshineSelectEntityDescription,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self.api = api
        self.scooter_id = scooter_id
        self.entity_description = description
        
        self._attr_unique_id = f"{scooter_id}_{description.key}"
        self._attr_options = description.options
        self._attr_current_option = description.options[0]
    
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
        """Return the name of the select entity."""
        scooter = self.coordinator.data[self.scooter_id]
        return f"{scooter.get('vin', self.scooter_id)} {self.entity_description.name}"
    
    @property
    def current_option(self) -> str | None:
        """Return the selected entity option."""
        # If the API provides current state, use it
        scooter = self.coordinator.data[self.scooter_id]
        state_key = f"{self.entity_description.key}_state"
        if state_key in scooter:
            return scooter[state_key]
        return self._attr_current_option
    
    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            api_method = getattr(self.api, self.entity_description.api_method)
            await api_method(self.scooter_id, option)
            self._attr_current_option = option
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(
                "Failed to set %s to %s for scooter %s: %s",
                self.entity_description.key,
                option,
                self.scooter_id,
                err
            )
            raise