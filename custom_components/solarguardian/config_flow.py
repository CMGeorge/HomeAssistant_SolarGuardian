"""Config flow for SolarGuardian integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_DOMAIN
from homeassistant.data_entry_flow import FlowResult

from .api import SolarGuardianAPI, SolarGuardianAPIError
from .const import (
    CONF_APP_KEY,
    CONF_APP_SECRET,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    DOMAIN_CHINA,
    DOMAIN_INTERNATIONAL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DOMAIN, default=DOMAIN_INTERNATIONAL): vol.In(
            {
                DOMAIN_CHINA: "China (openapi.epsolarpv.com)",
                DOMAIN_INTERNATIONAL: "International (glapi.mysolarguardian.com)",
            }
        ),
        vol.Required(CONF_APP_KEY): str,
        vol.Required(CONF_APP_SECRET): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SolarGuardian."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            # Test authentication
            api = SolarGuardianAPI(
                domain=user_input[CONF_DOMAIN],
                app_key=user_input[CONF_APP_KEY],
                app_secret=user_input[CONF_APP_SECRET],
            )

            await api.authenticate()
            await api.close()

        except SolarGuardianAPIError as err:
            _LOGGER.error("Authentication failed: %s", err)
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"

        if not errors:
            # Create a unique ID based on the app key
            await self.async_set_unique_id(user_input[CONF_APP_KEY])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"SolarGuardian ({user_input[CONF_DOMAIN]})",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for SolarGuardian."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        super().__init__(config_entry)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
                }
            ),
        )
