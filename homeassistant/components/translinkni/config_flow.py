"""Config flow for Translink NI integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import DOMAIN
from .platform import TranslinkPlatform

_LOGGER = logging.getLogger(__name__)

STEP_AUTH_DATA_SCHEMA = vol.Schema({vol.Required("api_token"): str})


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow handler for updating integration settings."""

    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        """Initilise the options flow."""
        self.conf = entry
        self.state: dict[str, Any] = {}

    async def async_step_init(self, input: dict[str, Any] | None = None) -> FlowResult:
        """Init flow."""
        return await self.async_step_add_journey_1_search()

    async def async_step_add_journey_1_search(
        self, input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add journey."""
        if input is None:
            return self.async_show_form(
                step_id="add_journey_1_search",
                data_schema=vol.Schema(
                    {vol.Required("origin"): str, vol.Required("destination"): str}
                ),
            )

        self.state = input
        return await self.async_step_add_journey_2_choose()

    async def async_step_add_journey_2_choose(
        self, input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Choose stops from search results."""
        if input is None:
            api = TranslinkPlatform(self.conf.data["api_token"])
            origins = await api.find_stops(self.state["origin"])
            dests = await api.find_stops(self.state["destination"])
            api.close()
            self.state = {"origins": origins, "dests": dests}
            originOptions = [
                SelectOptionDict(value=o.toJson(), label=o.getName()) for o in origins
            ]
            destOptions = [
                SelectOptionDict(value=d.toJson(), label=d.getName()) for d in dests
            ]
            return self.async_show_form(
                step_id="add_journey_2_choose",
                data_schema=vol.Schema(
                    {
                        vol.Required("origin"): SelectSelector(
                            SelectSelectorConfig(
                                options=originOptions, mode=SelectSelectorMode.DROPDOWN
                            )
                        ),
                        vol.Required("destination"): SelectSelector(
                            SelectSelectorConfig(
                                options=destOptions, mode=SelectSelectorMode.DROPDOWN
                            )
                        ),
                    }
                ),
            )

        origin = TranslinkPlatform.location_from_json(input["origin"])
        dest = TranslinkPlatform.location_from_json(input["destination"])

        title = f"{origin.getName()} -> {dest.getName()}"
        data = {
            "title": title,
            "origin": input["origin"],
            "dest": input["destination"],
        }
        return self.async_create_entry(title=title, data=data)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    hub = TranslinkPlatform(data["api_token"])

    if not await hub.test_authenticate():
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "Translink NI"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Translink NI."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_AUTH_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create options flow."""
        return OptionsFlowHandler(config_entry)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
