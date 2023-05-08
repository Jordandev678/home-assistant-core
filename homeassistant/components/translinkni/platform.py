"""Platform class for the translink integration."""
from aiohttp import ClientSession
from translinkni import TLLocation, TranslinkNIAPI


class TranslinkPlatform:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, token: str) -> None:
        """Initialize."""
        self.session = ClientSession(base_url=TranslinkNIAPI.HOST)
        self.client = TranslinkNIAPI(self.session, token)

    async def test_authenticate(self) -> bool:
        """Test if we can authenticate with the host."""
        try:
            stops = await self.client.findStops("Belfast")
            return len(stops) > 0
        except RuntimeError:
            return False

    async def find_stops(self, name):
        """Find all the stops matching name."""
        return await self.client.findStops(name)

    def close(self):
        """Close the session associated with this platform instance."""
        self.session.close()

    @staticmethod
    def location_from_json(json) -> TLLocation:
        """Get a TLLocation back from its toJson call."""
        return TLLocation.fromJson(json)
