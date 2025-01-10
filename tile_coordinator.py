"""Module for coordinating tile fetching and caching operations."""

from __future__ import annotations

import asyncio
import pygame
from typing import Optional, Tuple

from coordinates import CoordinateManager
from cache_manager import CacheManager
from tile_fetcher import TileFetcher
from background_loader import BackgroundLoader

class TileCoordinator:
    """Coordinates tile fetching, caching, and background loading operations."""

    def __init__(self) -> None:
        """Initialize the tile coordinator."""
        self.coordinate_manager = CoordinateManager()
        self.cache_manager = CacheManager()
        self.tile_fetcher = TileFetcher()
        self.background_loader = BackgroundLoader()

        # Initialize background loader
        self.background_loader.set_fetch_callback(self.fetch_tile)

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

    def preload_surrounding_tiles(self, x: int, y: int, zoom: int) -> None:
        """Add surrounding tiles to the preload queue.

        Args:
            x: Center tile x coordinate
            y: Center tile y coordinate
            zoom: Zoom level
        """
        self.background_loader.preload_surrounding_tiles(x, y, zoom)

    def ensure_background_loader(self, loop: asyncio.AbstractEventLoop) -> None:
        """Ensure the background loader is running.

        Args:
            loop: Event loop to run the background loader on
        """
        self.background_loader.ensure_background_loader(loop)

    async def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            await self.tile_fetcher.cleanup()
            self.background_loader.cleanup()
        except Exception as e:
            print(f"Error during tile coordinator cleanup: {e}")
