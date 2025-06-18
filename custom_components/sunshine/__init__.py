"""The Sunshine Scooter integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SunshineAPI
from .const import ATTR_DURATION, DOMAIN
from .coordinator import SunshineDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.BUTTON,
    Platform.DEVICE_TRACKER,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sunshine from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    session = async_get_clientsession(hass)
    api = SunshineAPI(
        entry.data["token"], 
        entry.data.get("base_url", "https://rescoot.org"),
        session
    )
    
    try:
        await api.test_authentication()
    except Exception as err:
        raise ConfigEntryAuthFailed from err
    
    coordinator = SunshineDataUpdateCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register services
    async def handle_trigger_alarm(call: ServiceCall) -> None:
        """Handle trigger alarm service call."""
        entity_id = call.data[ATTR_ENTITY_ID][0]
        duration = call.data[ATTR_DURATION]
        
        # Extract scooter_id from entity_id
        scooter_id = entity_id.split(".")[-1].replace("_lock", "")
        
        await api.trigger_alarm(scooter_id, duration)
        await coordinator.async_request_refresh()
    
    async def handle_request_telemetry(call: ServiceCall) -> None:
        """Handle request telemetry service call."""
        entity_id = call.data[ATTR_ENTITY_ID][0]
        
        # Extract scooter_id from entity_id
        scooter_id = entity_id.split(".")[-1].replace("_lock", "")
        
        await api.request_telemetry(scooter_id)
        await coordinator.async_request_refresh()
    
    async def handle_update_firmware(call: ServiceCall) -> None:
        """Handle update firmware service call."""
        entity_id = call.data[ATTR_ENTITY_ID][0]
        
        # Extract scooter_id from entity_id
        scooter_id = entity_id.split(".")[-1].replace("_lock", "")
        
        await api.update_firmware(scooter_id)
    
    hass.services.async_register(
        DOMAIN,
        "trigger_alarm",
        handle_trigger_alarm,
        schema=vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
            vol.Required(ATTR_DURATION): cv.string,
        }),
    )
    
    hass.services.async_register(
        DOMAIN,
        "request_telemetry",
        handle_request_telemetry,
        schema=vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        }),
    )
    
    hass.services.async_register(
        DOMAIN,
        "update_firmware",
        handle_update_firmware,
        schema=vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        }),
    )
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # Unregister services if this is the last config entry
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "trigger_alarm")
            hass.services.async_remove(DOMAIN, "request_telemetry")
            hass.services.async_remove(DOMAIN, "update_firmware")
    
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)