"""Module for managing tile scaling calculations."""

from managers.viewport_manager import ViewportManager


class TileScalingManager:
    """Handles all tile scaling calculations."""

    def __init__(self, base_tile_size: int = 256) -> None:
        """Initialize the tile scaling manager.

        Args:
            base_tile_size: Base size of map tiles in pixels (default: 256)
        """
        self.base_tile_size = base_tile_size
    def get_tile_size(self, tile_zoom: int) -> float:
        """Calculate the scaled size of tiles based on viewport zoom level.

        Args:
            viewport: The viewport manager controlling the view
            tile_zoom: Current zoom level for tile detail

        Returns:
            Scaled size of tiles for rendering
        """
        return self.base_tile_size * (1 / 2)  ** (tile_zoom - 1)
    
    def get_scaled_tile_size(self, viewport: ViewportManager, tile_zoom: int) -> float:
        """Calculate the scaled size of tiles based on viewport zoom level.

        Args:
            viewport: The viewport manager controlling the view
            tile_zoom: Current zoom level for tile detail

        Returns:
            Scaled size of tiles for rendering
        """
        return self.base_tile_size * viewport.state.zoom * (1 / 2)  ** (tile_zoom - 1)
    
    def get_world_coordinates(
        self, tile_x: int, tile_y: int
    ) -> tuple[float, float]:
        """Calculate world coordinates for a tile.

        Args:
            tile_x: Tile's x-coordinate
            tile_y: Tile's y-coordinate
            tile_size_scaled: Current scaled size of tiles

        Returns:
            Tuple of (x, y) world coordinates for the tile
        """
        return tile_x *  self.base_tile_size, tile_y *  self.base_tile_size
