"""Select platform for Sunshine Scooter integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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
from .entity import SunshineEntity

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True, kw_only=True)
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


class SunshineSelect(SunshineEntity, SelectEntity):
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
        super().__init__(coordinator, scooter_id)
        self.api = api
        self.entity_description = description
        
        self._attr_unique_id = f"{scooter_id}_{description.key}"
        self._attr_options = description.options
        self._attr_current_option = description.options[0]
    
    @property
    def current_option(self) -> str | None:
        """Return the selected entity option."""
        if scooter_data := self.coordinator.data.get(self.scooter_id):
            if self.entity_description.key == "blinkers":
                return scooter_data.get(self.entity_description.key, BLINKER_OFF)
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