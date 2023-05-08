"""Sensor module to show the timetable for a route."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

SCAN_INTERVAL = timedelta(hours=1)
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Aladdin Connect sensor devices."""

    hass.data[DOMAIN][entry.entry_id]

    # entities = [
    #    TranslinkSensor(api, journey["origin"], journey["destination"])
    #    for journey in entry["journeys"]
    # ]
    # async_add_entities(entities)
    return


class TranslinkSensor(SensorEntity):
    """Translink NI sensor for a route."""

    def __init__(self, api, originid, destid) -> None:
        """Initialise for route."""
        super().__init__()
        self._api = api
        self._origin = originid
        self._dest = destid
        self._state = None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._origin} -> {self._dest}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self) -> None:
        """Update the sensor."""
        pass
