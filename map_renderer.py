"""Module for handling map rendering operations."""

from __future__ import annotations

import pygame
from typing import List, Optional

from async_tile_loader import TileCoordinate
from tile_renderer import TileRenderer
from managers.viewport_manager import ViewportManager
from tile_scaling import TileScalingManager


class MapRenderer:
    """Handles the rendering of map tiles and coordinates with the viewport."""

    TILE_SIZE: int = 256  # Standard OSM tile size

    def __init__(self, window_width: int, window_height: int) -> None:
        """Initialize the map renderer.

        Args:
            window_width: Width of the window in pixels
            window_height: Height of the window in pixels
        """
        self.tile_renderer = TileRenderer(window_width, window_height)
        self._window_width = window_width
        self._window_height = window_height
        self._tile_zoom = 1
        self._zoom = 1
        self.scaling_manager = TileScalingManager(self.TILE_SIZE)

    def update_zoom(self, viewport: ViewportManager) -> None:
        """Update zoom levels based on viewport state.

        Args:
            viewport: The viewport manager containing current view state
        """
        self._tile_zoom = int(viewport.state.zoom)
        self._zoom = viewport.state.zoom % self._tile_zoom

    def prepare_visible_tiles(self, viewport: ViewportManager) -> List[TileCoordinate]:
        """Calculate visible tiles and their scaled size.

        Args:
            viewport: Current viewport state

        Returns:
            Tuple of (list of visible tile coordinates, scaled tile size)
        """
        visible_data = self.tile_renderer.calculate_visible_tiles(
            viewport, self._tile_zoom
        )
        tiles_to_load = [
            TileCoordinate(x, y, zoom) for x, y, zoom in visible_data.tiles
        ]
        return tiles_to_load

    def render_tile(
        self,
        screen: pygame.Surface,
        tile: pygame.Surface,
        coord: TileCoordinate,
        viewport: ViewportManager,
    ) -> None:
        """Render a single tile to the screen.

        Args:
            screen: Surface to draw on
            tile: The tile surface to render
            coord: Coordinates of the tile
            viewport: Current viewport
        """
        # Calculate scaled tile size for rendering
        tile_size_scaled = self.scaling_manager.get_scaled_tile_size(
            viewport, self._tile_zoom
        )
        position = self.tile_renderer.get_screen_position(
            coord.x, coord.y, tile_size_scaled, viewport
        )
        self.tile_renderer.render_tile(screen, tile, position, tile_size_scaled)

    def render_loaded_tiles(
        self,
        screen: pygame.Surface,
        tiles: List[Optional[pygame.Surface]],
        coords: List[TileCoordinate],
        # tile_size_scaled: float,
        viewport: ViewportManager,
    ) -> None:
        """Render a batch of loaded tiles to the screen.

        Args:
            screen: Surface to draw on
            tiles: List of loaded tile surfaces
            coords: List of tile coordinates
            tile_size_scaled: Scaled tile size
            viewport: Current viewport
        """

        for tile, coord in zip(tiles, coords):
            if tile:
                self.render_tile(screen, tile, coord, viewport)
