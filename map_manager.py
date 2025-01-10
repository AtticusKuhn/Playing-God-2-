"""Map Manager module for coordinating map components.

This module provides the MapManager class which acts as a facade to coordinate
the various components of the map system.
"""

from __future__ import annotations

import pygame

from async_tile_loader import AsyncTileLoader
from tile_coordinator import TileCoordinator
from map_renderer import MapRenderer
from managers.viewport_manager import ViewportManager


class MapManager:
    """Coordinates the map system components.

    This class acts as a facade, delegating operations to specialized components
    for async loading, tile coordination, and rendering.
    """

    def __init__(self, window_width: int, window_height: int) -> None:
        """Initialize the MapManager with the specified window dimensions.

        Args:
            window_width: Width of the window in pixels
            window_height: Height of the window in pixels
        """
        # Initialize specialized components
        self.async_loader = AsyncTileLoader()
        self.tile_coordinator = TileCoordinator()
        self.map_renderer = MapRenderer(window_width, window_height)

        # Store window dimensions
        self._window_width = window_width
        self._window_height = window_height

    def update(self, viewport: ViewportManager) -> None:
        """Update map state based on viewport.

        Args:
            viewport: The viewport manager containing current view state
        """
        self.map_renderer.update_zoom(viewport)

    def draw(self, screen: pygame.Surface, viewport: ViewportManager) -> None:
        """Draw the map to the screen.

        Args:
            screen: Pygame surface to draw on
            viewport: Current viewport state
        """
        # Ensure background loader is running
        self.tile_coordinator.ensure_background_loader(self.async_loader._loop)

        # Calculate visible tiles
        tiles_to_load = self.map_renderer.prepare_visible_tiles(viewport)

        # Separate tiles into cached and uncached
        uncached_tiles = []
        for coord in tiles_to_load:
            # Add to preload queue for surrounding tiles
            self.tile_coordinator.preload_surrounding_tiles(
                coord.x, coord.y, coord.zoom
            )

            # Check if tile is already in cache
            if tile := self.tile_coordinator.cache_manager.get_from_memory(
                coord.x, coord.y, coord.zoom
            ):
                self.map_renderer.render_tile(screen, tile, coord, viewport)
            else:
                uncached_tiles.append(coord)

        # Load uncached tiles asynchronously
        if uncached_tiles:
            if loaded_tiles := self.async_loader.load_tiles_threadsafe(
                uncached_tiles, self.tile_coordinator.fetch_tile
            ):
                self.map_renderer.render_loaded_tiles(
                    screen, loaded_tiles, uncached_tiles, viewport
                )

    async def cleanup(self) -> None:
        """Cleanup resources asynchronously."""
        try:
            await self.async_loader.cleanup()
            await self.tile_coordinator.cleanup()
        except Exception as e:
            print(f"Error during cleanup: {e}")
