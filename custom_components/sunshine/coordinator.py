"""Data update coordinator for Sunshine Scooter integration."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SunshineAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=30)


class SunshineDataUpdateCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Class to manage fetching Sunshine data from the API."""
    
    def __init__(
        self,
        hass: HomeAssistant,
        api: SunshineAPI,
    ) -> None:
        """Initialize the data update coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.api = api
    
    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Update data via API."""
        try:
            scooters = await self.api.get_scooters()
            
            # Create a dictionary keyed by scooter ID for easy lookup
            data = {}
            for scooter in scooters:
                data[scooter["id"]] = scooter
            
            return data
        except Exception as err:
            raise UpdateFailed(f"Failed to fetch scooter data: {err}") from err