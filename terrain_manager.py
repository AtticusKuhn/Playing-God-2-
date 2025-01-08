import aiohttp
from typing import Dict, Optional
from coordinates import CoordinateManager


class TerrainManager:
    def __init__(self, tile_size: int = 256):
        self.coordinate_manager = CoordinateManager()
        self.water_boundaries_cache: Dict[str, bool] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.tile_size = tile_size

    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def is_water(self, x: float, y: float, zoom: int) -> bool:
        """Check if a given coordinate is water."""
        # Convert game coordinates to lat/lon
        lat, lon = self.coordinate_manager.pixel_to_lat_lng(x, y, zoom, self.tile_size)
        cache_key = f"{lat:.6f},{lon:.6f}"

        # Check cache first
        if cache_key in self.water_boundaries_cache:
            return self.water_boundaries_cache[cache_key]

        # Query Overpass API for water features
        query = f"""
        [out:json];
        way(around:100,{lat},{lon})[natural=water];
        out geom;
        """

        try:
            session = await self.get_session()
            async with session.post(
                "http://overpass-api.de/api/interpreter", data=query
            ) as response:
                if response.status == 200:
                    data = await response.json()

                    # Check if point is within any water features
                    is_water = False
                    for element in data.get("elements", []):
                        if element.get("type") == "way":
                            geometry = element.get("geometry", [])
                            points = [(node["lat"], node["lon"]) for node in geometry]
                            if len(points) > 2 and self._point_in_polygon(
                                lat, lon, points
                            ):
                                is_water = True
                                break

                    # Cache the result
                    self.water_boundaries_cache[cache_key] = is_water
                    return is_water

        except Exception as e:
            print(f"Error checking water boundaries: {e}")
            # If there's an error, assume it's not water to be safe
            return False

        return False

    def _point_in_polygon(self, lat: float, lon: float, polygon: list) -> bool:
        """Ray casting algorithm to determine if a point is inside a polygon."""
        inside = False
        j = len(polygon) - 1

        for i in range(len(polygon)):
            if (polygon[i][1] > lon) != (polygon[j][1] > lon) and (
                lat
                < (polygon[j][0] - polygon[i][0])
                * (lon - polygon[i][1])
                / (polygon[j][1] - polygon[i][1])
                + polygon[i][0]
            ):
                inside = not inside
            j = i

        return inside

    async def cleanup(self):
        """Cleanup resources."""
        if self.session and not self.session.closed:
            await self.session.close()
