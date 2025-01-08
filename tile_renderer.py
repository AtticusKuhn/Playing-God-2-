"""Module for rendering map tiles in a scrollable viewport."""
from dataclasses import dataclass
from typing import Tuple, List, NamedTuple
import pygame
import math


class VisibleTileData(NamedTuple):
    """Data structure for visible tile information."""
    tiles: List[Tuple[int, int, int]]  # List of (x, y, zoom) tuples
    scaled_size: float  # Scaled size of tiles for rendering


class TileRenderer:
    """Handles the rendering of map tiles based on viewport position and zoom level."""
    
    # Number of extra tiles to load in each direction for smooth scrolling
    BUFFER_TILES: int = 2
    DEFAULT_TILE_SIZE: int = 256

    def __init__(self, window_width: int, window_height: int, tile_size: int = DEFAULT_TILE_SIZE) -> None:
        """Initialize the tile renderer.
        
        Args:
            window_width: Width of the game window in pixels
            window_height: Height of the game window in pixels
            tile_size: Base size of map tiles in pixels (default: 256)
        """
        self.window_width = window_width
        self.window_height = window_height
        self.tile_size = tile_size

    def calculate_visible_tiles(
        self, viewport: 'ViewportManager', tile_zoom: int
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
        start_x = math.floor(left / self.tile_size) - self.BUFFER_TILES
        start_y = math.floor(top / self.tile_size) - self.BUFFER_TILES
        end_x = math.ceil(right / self.tile_size) + self.BUFFER_TILES
        end_y = math.ceil(bottom / self.tile_size) + self.BUFFER_TILES

        # Calculate scaled tile size for rendering
        scaled_tile_size = self.tile_size * viewport.state.zoom

        # Generate list of visible tiles using list comprehension
        visible_tiles = [
            (x, y, tile_zoom)
            for y in range(start_y, end_y)
            for x in range(start_x, end_x)
        ]

        return VisibleTileData(visible_tiles, scaled_tile_size)

    def get_screen_position(
        self, tile_x: int, tile_y: int, tile_size_scaled: float, viewport: 'ViewportManager'
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
        # Use unscaled tile size for world coordinates
        world_x = tile_x * self.tile_size
        world_y = tile_y * self.tile_size
        return viewport.world_to_screen(world_x, world_y)

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
        if tile_size_scaled != self.tile_size:
            scaled_size = int(tile_size_scaled)
            return pygame.transform.scale(tile, (scaled_size, scaled_size))
        return tile

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
        screen.blit(scaled_tile, position)
