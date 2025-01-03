import pygame
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from coordinates import CoordinateManager
from cache_manager import CacheManager
from tile_fetcher import TileFetcher
from tile_renderer import TileRenderer
from background_loader import BackgroundLoader
from managers.viewport_manager import ViewportManager

class MapManager:
    def __init__(self, window_width: int, window_height: int):
        # Initialize components
        self.coordinate_manager = CoordinateManager()
        self.cache_manager = CacheManager()
        self.tile_fetcher = TileFetcher()
        self.tile_renderer = TileRenderer(window_width, window_height)
        self.background_loader = BackgroundLoader()
        # self.viewport = viewport

        # Window properties
        self.window_width = window_width
        self.window_height = window_height
        self.tile_size = 256  # Standard OSM tile size

        # View state
        # self.base_lat = 51.5074  # London
        # self.base_lon = -0.1278
        # self.zoom_level = 2  # Initial zoom level
        # self.view_x = 0
        # self.view_y = 0
        self.tile_zoom = 2

        # Async setup
        self.loop = asyncio.get_event_loop()
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Set up background loader callback
        self.background_loader.set_fetch_callback(self.fetch_tile)

    async def fetch_tile(self, x: int, y: int, zoom: int) -> Optional[pygame.Surface]:
        """Fetch a single tile, using cache if available."""
        # Check caches first
        tile = self.cache_manager.get_from_memory(x, y, zoom)
        if tile:
            return tile

        tile = self.cache_manager.get_from_disk(x, y, zoom)
        if tile:
            return tile

        # Wait if rate limited
        while self.tile_fetcher.is_rate_limited():
            await asyncio.sleep(0.1)

        # Fetch from network
        url = self.coordinate_manager.get_tile_url(x, y, zoom)
        data = await self.tile_fetcher.fetch_tile_data(url)
        if data:
            return self.cache_manager.save_to_cache(x, y, zoom, data)
        return None

    def update(self, viewport: ViewportManager):
        """Update map state based on viewport"""
        # self.viewport = viewport
        # Convert game zoom level (0.5-5.0) to a smoother OSM zoom level (1-8)
        # self.zoom_level = max(1.0, min(8.0, 1.0 + (self.viewport.state.zoom - 0.5) * (7.0 / 4.5)))
        # Calculate the base OSM zoom level for tile fetching
        self.tile_zoom = int(viewport.state.zoom)
        pass

    def draw(self, screen: pygame.Surface, viewport):
        """Draw visible map tiles to the screen"""
        # Calculate visible tiles and their scaled size
        visible_tiles, tile_size_scaled = self.tile_renderer.calculate_visible_tiles(
            viewport, self.tile_zoom
        )

        # Ensure background loader is running
        self.background_loader.ensure_background_loader(self.loop)

        # Create batch of tiles to load
        tiles_to_load = []
        for x, y, zoom in visible_tiles:
            # Add to preload queue for surrounding tiles
            self.background_loader.preload_surrounding_tiles(x, y, zoom)

            # Get tile from cache or add to load batch
            tile = self.cache_manager.get_from_memory(x, y, zoom)
            if tile is None:
                tiles_to_load.append((x, y, zoom))
                continue

            # Draw cached tile
            position = self.tile_renderer.get_screen_position(
                x, y, tile_size_scaled, viewport
            )
            self.tile_renderer.render_tile(screen, tile, position, tile_size_scaled)

        # Load missing tiles asynchronously
        if tiles_to_load:

            async def load_batch():
                tasks = [self.fetch_tile(x, y, z) for x, y, z in tiles_to_load]
                return await asyncio.gather(*tasks)

            future = asyncio.run_coroutine_threadsafe(load_batch(), self.loop)
            try:
                # Wait for a short timeout to avoid blocking the game
                tiles = future.result(timeout=0.01)
                # Draw newly loaded tiles
                for tile, (x, y, z) in zip(tiles, tiles_to_load):
                    if tile:
                        position = self.tile_renderer.get_screen_position(
                            x, y, tile_size_scaled, self.viewport
                        )
                        self.tile_renderer.render_tile(
                            screen, tile, position, tile_size_scaled
                        )
            except TimeoutError:
                # Timeout is expected for tiles that take too long to load
                pass

    def cleanup(self):
        """Cleanup resources."""
        asyncio.run_coroutine_threadsafe(self.tile_fetcher.cleanup(), self.loop)
        self.background_loader.cleanup()
        self.executor.shutdown(wait=False)
