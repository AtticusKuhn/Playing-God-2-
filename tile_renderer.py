import pygame
import math
from typing import Tuple, List


class TileRenderer:
    def __init__(self, window_width: int, window_height: int, tile_size: int = 256):
        self.window_width = window_width
        self.window_height = window_height
        self.tile_size = tile_size

    def calculate_visible_tiles(
        self, viewport, tile_zoom: int
    ) -> Tuple[List[Tuple[int, int, int]], float]:
        """Calculate which tiles are visible and need to be rendered."""
        # Use unscaled tile size for world coordinate calculations
        # Get viewport bounds in world coordinates
        left, top, right, bottom = viewport.get_visible_bounds()

        # Calculate the visible area bounds in tile coordinates
        start_x = math.floor(left / self.tile_size)
        start_y = math.floor(top / self.tile_size)
        end_x = math.ceil(right / self.tile_size)
        end_y = math.ceil(bottom / self.tile_size)

        # Calculate scaled tile size for rendering
        tile_size_scaled = self.tile_size * viewport.state.zoom

        # Add buffer tiles in each direction to handle partial visibility and smooth scrolling
        buffer = 2  # Number of extra tiles to load in each direction
        start_x -= buffer
        start_y -= buffer
        end_x += buffer
        end_y += buffer

        # Generate list of visible tiles
        visible_tiles = []
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                visible_tiles.append((x, y, tile_zoom))

        return visible_tiles, tile_size_scaled

    def get_screen_position(
        self,
        tile_x: int,
        tile_y: int,
        tile_size_scaled: float,
        viewport
    ) -> Tuple[float, float]:
        """Calculate the screen position for a tile."""
        # Use unscaled tile size for world coordinates
        world_x = tile_x * self.tile_size
        world_y = tile_y * self.tile_size
        return viewport.world_to_screen(world_x, world_y)

    def scale_tile(
        self, tile: pygame.Surface, tile_size_scaled: float
    ) -> pygame.Surface:
        """Scale a tile to the appropriate size if needed."""
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
    ):
        """Render a single tile to the screen."""
        scaled_tile = self.scale_tile(tile, tile_size_scaled)
        screen.blit(scaled_tile, position)
