from pyproj import Transformer

class CoordinateManager:
    def __init__(self):
        # Initialize projection transformer (Web Mercator to/from WGS84)
        self.transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
        
    def lat_lon_to_pixel(self, lat, lon, zoom, tile_size):
        """Convert latitude/longitude to pixel coordinates at a given zoom level"""
        n = 2.0 ** zoom
        x, y = self.transformer.transform(lon, lat)
        tile_x = (x + 20037508.34) / (40075016.68 / n)
        tile_y = (-y + 20037508.34) / (40075016.68 / n)
        return tile_x * tile_size, tile_y * tile_size

    @staticmethod
    def get_tile_url(x: int, y: int, zoom: int) -> str:
        """Get the URL for an OSM tile"""
        return f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"
