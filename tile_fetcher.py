import aiohttp
import time
from typing import Optional, List


class TileFetcher:
    def __init__(self, max_requests_per_second: int = 2):
        self.session: Optional[aiohttp.ClientSession] = None
        self.request_times: List[float] = []
        self.max_requests_per_second = max_requests_per_second

    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "User-Agent": "Python Game Version 1",
                    "From": "atticusmkuhn@gmail.com",
                }
            )
        return self.session

    def is_rate_limited(self) -> bool:
        """Check if we're currently rate limited."""
        now = time.time()
        self.request_times = [t for t in self.request_times if now - t < 1.0]
        return len(self.request_times) >= self.max_requests_per_second

    async def fetch_tile_data(self, url: str) -> Optional[bytes]:
        """Fetch tile data from the given URL."""
        print(f"fetching {url}")
        try:
            session = await self.get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.read()
                    self.request_times.append(time.time())
                    return data
        except Exception as e:
            print(f"Error fetching tile: {e}")
        return None

    async def cleanup(self):
        """Cleanup resources."""
        if self.session and not self.session.closed:
            await self.session.close()
