import pygame
from pathlib import Path
from typing import Dict, Tuple, Optional


class CacheManager:
    def __init__(self):
        self.memory_cache: Dict[Tuple[int, int, int], pygame.Surface] = {}
        self.disk_cache_dir = Path.home() / ".map_cache"
        self.disk_cache_dir.mkdir(exist_ok=True)

    def get_cache_path(self, x: int, y: int, zoom: int) -> Path:
        """Get the path for a cached tile."""
        return self.disk_cache_dir / f"tile_{zoom}_{x}_{y}.png"

    def get_from_memory(self, x: int, y: int, zoom: int) -> Optional[pygame.Surface]:
        """Get a tile from memory cache if it exists."""
        return self.memory_cache.get((x, y, zoom))

    def get_from_disk(self, x: int, y: int, zoom: int) -> Optional[pygame.Surface]:
        """Get a tile from disk cache if it exists."""
        cache_path = self.get_cache_path(x, y, zoom)
        if cache_path.exists():
            try:
                surface = pygame.image.load(str(cache_path))
                self.memory_cache[(x, y, zoom)] = surface
                return surface
            except Exception as e:
                print(f"Error loading cached tile: {e}")
        return None

    def save_to_cache(
        self, x: int, y: int, zoom: int, data: bytes
    ) -> Optional[pygame.Surface]:
        """Save tile data to both disk and memory cache."""
        try:
            # Save to disk cache
            cache_path = self.get_cache_path(x, y, zoom)
            with open(cache_path, "wb") as f:
                f.write(data)

            # Load into pygame and save to memory cache
            from io import BytesIO

            surface = pygame.image.load(BytesIO(data))
            self.memory_cache[(x, y, zoom)] = surface
            return surface
        except Exception as e:
            print(f"Error saving tile to cache: {e}")
            return None
