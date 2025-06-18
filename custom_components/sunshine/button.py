"""Button platform for Sunshine Scooter integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
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
class SunshineButtonEntityDescription(ButtonEntityDescription):
    """Describes Sunshine button entity."""
    
    press_fn: Callable[[Any, str], Any] | None = None
    press_kwargs: dict[str, Any] | None = None


BUTTON_TYPES: list[SunshineButtonEntityDescription] = [
    SunshineButtonEntityDescription(
        key="honk",
        name="Honk",
        icon="mdi:bullhorn",
        press_fn=lambda api, scooter_id: api.honk(scooter_id),
    ),
    SunshineButtonEntityDescription(
        key="locate",
        name="Locate",
        icon="mdi:map-marker",
        press_fn=lambda api, scooter_id: api.locate(scooter_id),
    ),
    SunshineButtonEntityDescription(
        key="ping",
        name="Ping",
        icon="mdi:access-point-network",
        press_fn=lambda api, scooter_id: api.ping(scooter_id),
    ),
    SunshineButtonEntityDescription(
        key="open_seatbox",
        name="Open Seatbox",
        icon="mdi:treasure-chest",
        press_fn=lambda api, scooter_id: api.open_seatbox(scooter_id),
    ),
    SunshineButtonEntityDescription(
        key="request_telemetry",
        name="Request Telemetry",
        icon="mdi:chart-line",
        press_fn=lambda api, scooter_id: api.request_telemetry(scooter_id),
    ),
    SunshineButtonEntityDescription(
        key="update_firmware",
        name="Update Firmware",
        icon="mdi:cellphone-arrow-down",
        press_fn=lambda api, scooter_id: api.update_firmware(scooter_id),
    ),
    SunshineButtonEntityDescription(
        key="alarm_5s",
        name="Alarm (5s)",
        icon="mdi:alarm-light",
        press_fn=lambda api, scooter_id: api.trigger_alarm(scooter_id, "5s"),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sunshine Scooter buttons."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    api = data["api"]
    coordinator = data["coordinator"]
    
    entities: list[SunshineButton] = []
    
    for scooter_id in coordinator.data:
        for description in BUTTON_TYPES:
            entities.append(
                SunshineButton(api, coordinator, scooter_id, description)
            )
    
    async_add_entities(entities)


class SunshineButton(SunshineEntity, ButtonEntity):
    """Representation of a Sunshine Scooter button."""
    
    entity_description: SunshineButtonEntityDescription
    
    def __init__(
        self,
        api,
        coordinator: SunshineDataUpdateCoordinator,
        scooter_id: str,
        description: SunshineButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, scooter_id)
        self.api = api
        self.entity_description = description
        self._attr_unique_id = f"{scooter_id}_{description.key}"
    
    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            if self.entity_description.press_fn:
                await self.entity_description.press_fn(self.api, self.scooter_id)
                await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(
                "Failed to press button %s for scooter %s: %s",
                self.entity_description.key,
                self.scooter_id,
                err
            )