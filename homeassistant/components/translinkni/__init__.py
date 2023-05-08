"""The Translink NI integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .platform import TranslinkPlatform

# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Translink NI from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    platform = TranslinkPlatform(entry.data["api_token"])
    # TODO: add an authorized check to throw ConfigEntryAuthFailed
    if not platform.test_authenticate():
        raise ConfigEntryNotReady("Error connecting to API")

    hass.data[DOMAIN][entry.entry_id] = platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
