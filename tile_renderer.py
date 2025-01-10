"""Module for rendering map tiles in a scrollable viewport."""

from typing import Tuple, List, NamedTuple
import pygame
import math
from managers.viewport_manager import ViewportManager
from tile_scaling import TileScalingManager


class VisibleTileData(NamedTuple):
    """Data structure for visible tile information."""

    tiles: List[Tuple[int, int, int]]  # List of (x, y, zoom) tuples
    # scaled_size: float  # Scaled size of tiles for rendering


class TileRenderer:
    """Handles the rendering of map tiles based on viewport position and zoom level."""

    # Number of extra tiles to load in each direction for smooth scrolling
    BUFFER_TILES: int = 2
    DEFAULT_TILE_SIZE: int = 256

    def __init__(
        self, window_width: int, window_height: int, tile_size: int = DEFAULT_TILE_SIZE
    ) -> None:
        """Initialize the tile renderer.

        Args:
            window_width: Width of the game window in pixels
            window_height: Height of the game window in pixels
            tile_size: Base size of map tiles in pixels (default: 256)
        """
        self.window_width = window_width
        self.window_height = window_height
        self.scaling_manager = TileScalingManager(tile_size)

    def calculate_visible_tiles(
        self, viewport: "ViewportManager", tile_zoom: int
    ) -> VisibleTileData:
        """Calculate which tiles are visible and need to be rendered.

        Args:
            viewport: The viewport manager controlling the view
            tile_zoom: Current zoom level for tile detail

        Returns:
            VisibleTileData containing list of visible tile coordinates and scaled tile size
        """
        left, top, right, bottom = viewport.get_visible_bounds()

        # Calculate tile coordinates from world coordinates
        start_x = (
            math.floor(left / self.scaling_manager.get_tile_size(tile_zoom)) - self.BUFFER_TILES
        )
        start_y = (
            math.floor(top / self.scaling_manager.get_tile_size(tile_zoom)) - self.BUFFER_TILES
        )
        end_x = (
            math.ceil(right / self.scaling_manager.get_tile_size(tile_zoom)) + self.BUFFER_TILES
        )
        end_y = (
            math.ceil(bottom / self.scaling_manager.get_tile_size(tile_zoom)) + self.BUFFER_TILES
        )

        # self.tile_size * viewport.state.zoom * (1 / 2) ** (tile_zoom - 1)

        # Generate list of visible tiles using list comprehension
        visible_tiles = [
            (x, y, tile_zoom)
            for y in range(start_y, end_y)
            for x in range(start_x, end_x)
        ]

        return VisibleTileData(visible_tiles)

    def get_screen_position(
        self,
        tile_x: int,
        tile_y: int,
        zoom: int,
        viewport: "ViewportManager",
    ) -> Tuple[float, float]:
        """Calculate the screen position for a tile.

        Args:
            tile_x: Tile's x-coordinate
            tile_y: Tile's y-coordinate
            tile_size_scaled: Current scaled size of tiles
            viewport: The viewport manager controlling the view

        Returns:
            Tuple of (x, y) screen coordinates for the tile
        """
        world_x, world_y = self.scaling_manager.get_world_coordinates(
            tile_x, tile_y
        )
        world_x *= (1 / 2) ** (zoom - 1)
        world_y *= (1 / 2) ** (zoom - 1)
        # Calculate relative position to camera
        rel_x = world_x - viewport.state.world_x
        rel_y = world_y - viewport.state.world_y

        # Apply zoom and center on screen
        screen_x = (rel_x * viewport.state.zoom) + (viewport.state.width / 2)
        screen_y = (rel_y * viewport.state.zoom) + (viewport.state.height / 2)

        return screen_x, screen_y
        # return viewport.world_to_screen(world_x, world_y)

    def scale_tile(
        self, tile: pygame.Surface, tile_size_scaled: float
    ) -> pygame.Surface:
        """Scale a tile surface to the appropriate size if needed.

        Args:
            tile: The tile surface to scale
            tile_size_scaled: Target size for the tile

        Returns:
            Scaled tile surface if scaling is needed, original surface otherwise
        """
        # if tile_size_scaled != self.scaling_manager.base_tile_size:
        #     scaled_size = int(tile_size_scaled)
        return pygame.transform.scale(tile, (tile_size_scaled, tile_size_scaled))
        # return tile

    def render_tile(
        self,
        screen: pygame.Surface,
        tile: pygame.Surface,
        position: Tuple[float, float],
        tile_size_scaled: float,
    ) -> None:
        """Render a single tile to the screen.

        Args:
            screen: The surface to render the tile on
            tile: The tile surface to render
            position: Screen coordinates to render the tile at
            tile_size_scaled: Current scaled size of tiles
        """
        scaled_tile = self.scale_tile(tile, tile_size_scaled)
        print(f"tile_size_scaled = {tile_size_scaled}")
        screen.blit(scaled_tile, position)
