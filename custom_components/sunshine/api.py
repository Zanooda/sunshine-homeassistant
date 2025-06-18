"""API client for Sunshine Scooter."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from .const import DEFAULT_BASE_URL

_LOGGER = logging.getLogger(__name__)


class SunshineAPI:
    """Sunshine API client."""
    
    def __init__(self, token: str, base_url: str, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self.token = token
        self.base_url = base_url.rstrip('/')
        self._session = session
        self._headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
    
    async def test_authentication(self) -> bool:
        """Test if the authentication is valid."""
        try:
            await self.get_scooters()
            return True
        except Exception as err:
            _LOGGER.error("Authentication test failed: %s", err)
            raise
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make a request to the API."""
        url = f"{self.base_url}/api/v1{endpoint}"
        
        async with self._session.request(method, url, headers=self._headers, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_scooters(self) -> list[dict[str, Any]]:
        """Get list of all scooters."""
        return await self._request("GET", "/scooters")
    
    async def get_scooter(self, scooter_id: str) -> dict[str, Any]:
        """Get details of a specific scooter."""
        return await self._request("GET", f"/scooters/{scooter_id}")
    
    async def get_config(self, vin: str) -> dict[str, Any]:
        """Get configuration for a specific scooter by VIN."""
        return await self._request("GET", f"/scooters/{vin}/config")
    
    async def unlock(self, scooter_id: str) -> dict[str, Any]:
        """Unlock a scooter."""
        return await self._request("POST", f"/scooters/{scooter_id}/unlock")
    
    async def lock(self, scooter_id: str) -> dict[str, Any]:
        """Lock a scooter."""
        return await self._request("POST", f"/scooters/{scooter_id}/lock")
    
    async def honk(self, scooter_id: str) -> dict[str, Any]:
        """Activate horn/honk sound."""
        return await self._request("POST", f"/scooters/{scooter_id}/honk")
    
    async def trigger_alarm(self, scooter_id: str, duration: str = "5s") -> dict[str, Any]:
        """Trigger alarm for specified duration."""
        return await self._request(
            "POST", 
            f"/scooters/{scooter_id}/alarm",
            json={"duration": duration}
        )
    
    async def play_sound(self, scooter_id: str, sound: str) -> dict[str, Any]:
        """Play different sound types."""
        return await self._request(
            "POST",
            f"/scooters/{scooter_id}/play_sound",
            json={"sound": sound}
        )
    
    async def blinkers(self, scooter_id: str, state: str) -> dict[str, Any]:
        """Control turn signal blinkers."""
        return await self._request(
            "POST",
            f"/scooters/{scooter_id}/blinkers",
            json={"state": state}
        )
    
    async def locate(self, scooter_id: str) -> dict[str, Any]:
        """Trigger location/find feature."""
        return await self._request("POST", f"/scooters/{scooter_id}/locate")
    
    async def ping(self, scooter_id: str) -> dict[str, Any]:
        """Ping scooter for connectivity check."""
        return await self._request("POST", f"/scooters/{scooter_id}/ping")
    
    async def request_telemetry(self, scooter_id: str) -> dict[str, Any]:
        """Request telemetry data from scooter."""
        return await self._request("POST", f"/scooters/{scooter_id}/request_telemetry")
    
    async def update_firmware(self, scooter_id: str) -> dict[str, Any]:
        """Initiate firmware update."""
        return await self._request("POST", f"/scooters/{scooter_id}/update_firmware")
    
    async def open_seatbox(self, scooter_id: str) -> dict[str, Any]:
        """Open the seat box/storage compartment."""
        return await self._request("POST", f"/scooters/{scooter_id}/open_seatbox")