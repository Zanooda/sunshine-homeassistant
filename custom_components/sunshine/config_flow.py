"""Config flow for Sunshine Scooter integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_TOKEN
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SunshineAPI
from .const import CONF_BASE_URL, DEFAULT_BASE_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_TOKEN): cv.string,
    vol.Optional(CONF_BASE_URL, default=DEFAULT_BASE_URL): cv.string,
})


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sunshine Scooter."""
    
    VERSION = 1
    
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            api = SunshineAPI(
                user_input[CONF_TOKEN],
                user_input.get(CONF_BASE_URL, DEFAULT_BASE_URL),
                session
            )
            
            try:
                await api.test_authentication()
            except Exception:
                errors["base"] = "invalid_auth"
            else:
                await self.async_set_unique_id(user_input[CONF_TOKEN][:8])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title="Sunshine Scooter",
                    data=user_input,
                )
        
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )