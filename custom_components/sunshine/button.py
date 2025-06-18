"""Button platform for Sunshine Scooter integration."""
from __future__ import annotations

import logging
from typing import Any, Callable

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
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
        key="make_noise",
        name="Make Noise",
        icon="mdi:volume-high",
        press_fn=lambda api, scooter_id: api.make_noise(scooter_id),
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


class SunshineButton(CoordinatorEntity[SunshineDataUpdateCoordinator], ButtonEntity):
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
        """Return the name of the button."""
        scooter = self.coordinator.data[self.scooter_id]
        return f"{scooter.get('vin', self.scooter_id)} {self.entity_description.name}"
    
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
            raise