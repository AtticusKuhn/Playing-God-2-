import asyncio
from typing import Set, Tuple, Optional, Callable
import pygame


class BackgroundLoader:
    def __init__(self):
        self.loading_queue: Set[Tuple[int, int, int]] = set()
        self.loading_task = None
        self.fetch_callback: Optional[Callable] = None

    def add_to_queue(self, x: int, y: int, zoom: int):
        """Add a tile to the loading queue."""
        self.loading_queue.add((x, y, zoom))

    def preload_surrounding_tiles(self, center_x: int, center_y: int, zoom: int):
        """Add surrounding tiles to the loading queue."""
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                x, y = center_x + dx, center_y + dy
                self.loading_queue.add((x, y, zoom))

    async def background_loader(self):
        """Background task to load queued tiles."""
        while True:
            if self.loading_queue and self.fetch_callback:
                x, y, zoom = self.loading_queue.pop()
                await self.fetch_callback(x, y, zoom)
            await asyncio.sleep(0.1)

    def ensure_background_loader(self, loop: asyncio.AbstractEventLoop):
        """Ensure the background loader is running."""
        if self.loading_task is None or self.loading_task.done():
            self.loading_task = asyncio.run_coroutine_threadsafe(
                self.background_loader(), loop
            )

    def set_fetch_callback(self, callback: Callable):
        """Set the callback function for fetching tiles."""
        self.fetch_callback = callback

    def cleanup(self):
        """Cleanup resources."""
        if self.loading_task:
            self.loading_task.cancel()
