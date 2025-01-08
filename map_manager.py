"""Map Manager module for handling tile-based map rendering and management.

This module provides the MapManager class which coordinates tile fetching,
caching, and rendering for an OpenStreetMap-based map system.
"""

from __future__ import annotations

import asyncio
import pygame
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Optional, Tuple, List, Any

from coordinates import CoordinateManager
from cache_manager import CacheManager
from tile_fetcher import TileFetcher
from tile_renderer import TileRenderer
from background_loader import BackgroundLoader
from managers.viewport_manager import ViewportManager


@dataclass
class TileCoordinate:
    """Represents a tile's coordinates and zoom level."""

    x: int
    y: int
    zoom: int


class MapManager:
    """Manages the map system including tile fetching, caching, and rendering.

    This class coordinates various components to provide a seamless map viewing
    experience, handling asynchronous tile loading, caching, and efficient
    rendering.
    """

    TILE_SIZE: int = 256  # Standard OSM tile size
    MAX_WORKERS: int = 4  # Maximum number of thread pool workers
    TILE_LOAD_TIMEOUT: float = 0.01  # Seconds to wait for tile loading

    def __init__(self, window_width: int, window_height: int) -> None:
        """Initialize the MapManager with the specified window dimensions.

        Args:
            window_width: Width of the window in pixels
            window_height: Height of the window in pixels
        """
        # Core components
        self.coordinate_manager = CoordinateManager()
        self.cache_manager = CacheManager()
        self.tile_fetcher = TileFetcher()
        self.tile_renderer = TileRenderer(window_width, window_height)
        self.background_loader = BackgroundLoader()

        # Window properties
        self._window_width = window_width
        self._window_height = window_height

        # View state
        self._tile_zoom = 1
        self._zoom = 1

        # Async setup
        self._loop = asyncio.get_event_loop()
        self._executor = ThreadPoolExecutor(max_workers=self.MAX_WORKERS)

        # Initialize background loader
        self.background_loader.set_fetch_callback(self.fetch_tile)

    @property
    def window_dimensions(self) -> Tuple[int, int]:
        """Get the current window dimensions."""
        return (self._window_width, self._window_height)

    async def fetch_tile(self, x: int, y: int, zoom: int) -> Optional[pygame.Surface]:
        """Fetch a single tile, using cache if available.

        Args:
            x: Tile x coordinate
            y: Tile y coordinate
            zoom: Zoom level

        Returns:
            Optional[pygame.Surface]: The tile surface if successful, None otherwise
        """
        try:
            # Try memory cache
            if tile := self.cache_manager.get_from_memory(x, y, zoom):
                return tile

            # Try disk cache
            if tile := self.cache_manager.get_from_disk(x, y, zoom):
                return tile

            # Handle rate limiting
            while self.tile_fetcher.is_rate_limited():
                await asyncio.sleep(0.1)

            # Fetch from network
            url = self.coordinate_manager.get_tile_url(x, y, zoom)
            if data := await self.tile_fetcher.fetch_tile_data(url):
                return self.cache_manager.save_to_cache(x, y, zoom, data)

            return None

        except Exception as e:
            print(f"Error fetching tile ({x}, {y}, {zoom}): {e}")
            return None

    def update(self, viewport: ViewportManager) -> None:
        """Update map state based on viewport.

        Args:
            viewport: The viewport manager containing current view state
        """
        self._tile_zoom = int(viewport.state.zoom)
        self._zoom = viewport.state.zoom % self._tile_zoom

    async def _load_tile_batch(self, tiles_to_load: List[TileCoordinate]) -> List[Any]:
        """Load a batch of tiles asynchronously.

        Args:
            tiles_to_load: List of tile coordinates to load

        Returns:
            List of loaded tiles
        """
        tasks = [
            self.fetch_tile(coord.x, coord.y, coord.zoom) for coord in tiles_to_load
        ]
        return await asyncio.gather(*tasks)

    def draw(self, screen: pygame.Surface, viewport: ViewportManager) -> None:
        """Draw visible map tiles to the screen.

        Args:
            screen: Pygame surface to draw on
            viewport: Current viewport state
        """
        # Calculate visible tiles
        visible_tiles, tile_size_scaled = self.tile_renderer.calculate_visible_tiles(
            viewport, self._tile_zoom
        )

        # Ensure background loader is running
        self.background_loader.ensure_background_loader(self._loop)

        # Process visible tiles
        tiles_to_load = []
        for x, y, zoom in visible_tiles:
            self._process_tile(
                screen, x, y, zoom, viewport, tile_size_scaled, tiles_to_load
            )

        # Load missing tiles asynchronously
        if tiles_to_load:
            self._handle_async_tile_loading(
                screen, tiles_to_load, tile_size_scaled, viewport
            )

    def _process_tile(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        zoom: int,
        viewport: ViewportManager,
        tile_size_scaled: int,
        tiles_to_load: List[TileCoordinate],
    ) -> None:
        """Process a single tile for rendering.

        Args:
            screen: Surface to draw on
            x: Tile x coordinate
            y: Tile y coordinate
            zoom: Zoom level
            viewport: Current viewport
            tile_size_scaled: Scaled tile size
            tiles_to_load: List to append tiles that need loading
        """
        # Add to preload queue for surrounding tiles
        self.background_loader.preload_surrounding_tiles(x, y, zoom)

        # Get tile from cache or add to load batch
        if tile := self.cache_manager.get_from_memory(x, y, zoom):
            position = self.tile_renderer.get_screen_position(
                x, y, self.TILE_SIZE, viewport
            )
            self.tile_renderer.render_tile(screen, tile, position, tile_size_scaled)
        else:
            tiles_to_load.append(TileCoordinate(x, y, zoom))

    def _handle_async_tile_loading(
        self,
        screen: pygame.Surface,
        tiles_to_load: List[TileCoordinate],
        tile_size_scaled: int,
        viewport: ViewportManager,
    ) -> None:
        """Handle asynchronous loading of tiles.

        Args:
            screen: Surface to draw on
            tiles_to_load: List of tiles to load
            tile_size_scaled: Scaled tile size
            viewport: Current viewport
        """
        future = asyncio.run_coroutine_threadsafe(
            self._load_tile_batch(tiles_to_load), self._loop
        )

        try:
            tiles = future.result(timeout=self.TILE_LOAD_TIMEOUT)
            self._render_loaded_tiles(
                screen, tiles, tiles_to_load, tile_size_scaled, viewport
            )
        except TimeoutError:
            # Expected for tiles that take too long to load
            pass
        except Exception as e:
            print(f"Error loading tiles: {e}")

    def _render_loaded_tiles(
        self,
        screen: pygame.Surface,
        tiles: List[Optional[pygame.Surface]],
        coords: List[TileCoordinate],
        tile_size_scaled: int,
        viewport: ViewportManager,
    ) -> None:
        """Render newly loaded tiles to the screen.

        Args:
            screen: Surface to draw on
            tiles: List of loaded tile surfaces
            coords: List of tile coordinates
            tile_size_scaled: Scaled tile size
            viewport: Current viewport
        """
        for tile, coord in zip(tiles, coords):
            if tile:
                position = self.tile_renderer.get_screen_position(
                    coord.x, coord.y, tile_size_scaled, viewport
                )
                self.tile_renderer.render_tile(screen, tile, position, tile_size_scaled)

    async def cleanup(self) -> None:
        """Cleanup resources asynchronously."""
        try:
            await self.tile_fetcher.cleanup()
            self.background_loader.cleanup()
            self._executor.shutdown(wait=False)
        except Exception as e:
            print(f"Error during cleanup: {e}")
