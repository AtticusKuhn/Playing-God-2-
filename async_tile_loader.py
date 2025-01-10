"""Module for handling asynchronous tile loading operations."""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Optional, List, Any, Callable
import pygame

@dataclass
class TileCoordinate:
    """Represents a tile's coordinates and zoom level."""
    x: int
    y: int
    zoom: int

class AsyncTileLoader:
    """Handles asynchronous loading of map tiles."""

    MAX_WORKERS: int = 4
    TILE_LOAD_TIMEOUT: float = 0.01

    def __init__(self) -> None:
        """Initialize the async tile loader."""
        self._loop = asyncio.get_event_loop()
        self._executor = ThreadPoolExecutor(max_workers=self.MAX_WORKERS)

    async def load_tile_batch(
        self, 
        tiles_to_load: List[TileCoordinate], 
        fetch_callback: Callable[[int, int, int], Optional[pygame.Surface]]
    ) -> List[Any]:
        """Load a batch of tiles asynchronously.

        Args:
            tiles_to_load: List of tile coordinates to load
            fetch_callback: Callback function to fetch individual tiles

        Returns:
            List of loaded tiles
        """
        tasks = [
            fetch_callback(coord.x, coord.y, coord.zoom) for coord in tiles_to_load
        ]
        return await asyncio.gather(*tasks)

    def load_tiles_threadsafe(
        self,
        tiles_to_load: List[TileCoordinate],
        fetch_callback: Callable[[int, int, int], Optional[pygame.Surface]]
    ) -> Optional[List[Any]]:
        """Load tiles in a thread-safe manner.

        Args:
            tiles_to_load: List of tile coordinates to load
            fetch_callback: Callback function to fetch individual tiles

        Returns:
            Optional list of loaded tiles
        """
        future = asyncio.run_coroutine_threadsafe(
            self.load_tile_batch(tiles_to_load, fetch_callback), 
            self._loop
        )

        try:
            return future.result(timeout=self.TILE_LOAD_TIMEOUT)
        except TimeoutError:
            return None
        except Exception as e:
            print(f"Error loading tiles: {e}")
            return None

    async def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            self._executor.shutdown(wait=False)
        except Exception as e:
            print(f"Error during async loader cleanup: {e}")
