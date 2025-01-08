"""Viewport manager for handling screen space calculations and transformations."""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class ViewportState:
    """Represents the current state of the viewport."""

    width: int
    height: int
    world_x: float  # Camera position in world space
    world_y: float
    zoom: float

    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        """Get the viewport bounds in world space.

        Returns:
            Tuple[float, float, float, float]: (left, top, right, bottom)
        """
        # Calculate the size of the viewport in world space
        world_width = self.width / self.zoom
        world_height = self.height / self.zoom

        # Calculate bounds
        left = self.world_x - (world_width / 2)
        right = self.world_x + (world_width / 2)
        top = self.world_y - (world_height / 2)
        bottom = self.world_y + (world_height / 2)

        return (left, top, right, bottom)


class ViewportManager:
    """Manages viewport transformations and coordinate conversions."""

    def __init__(self, width: int, height: int):
        """Initialize the viewport manager.

        Args:
            width: Width of the viewport in pixels
            height: Height of the viewport in pixels
        """
        self.state = ViewportState(
            width=width, height=height, world_x=0, world_y=0, zoom=1.0
        )

    def update(self, camera_x: float, camera_y: float, zoom: float) -> None:
        """Update the viewport state with new camera parameters.

        Args:
            camera_x: Camera x position in world space
            camera_y: Camera y position in world space
            zoom: Camera zoom level
        """
        self.state.world_x = camera_x
        self.state.world_y = camera_y
        self.state.zoom = zoom

    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """Convert world coordinates to screen coordinates.

        Args:
            world_x: X coordinate in world space
            world_y: Y coordinate in world space

        Returns:
            Tuple[float, float]: (screen_x, screen_y)
        """
        # Calculate relative position to camera
        rel_x = world_x - self.state.world_x
        rel_y = world_y - self.state.world_y

        # Apply zoom and center on screen
        screen_x = (rel_x * self.state.zoom) + (self.state.width / 2)
        screen_y = (rel_y * self.state.zoom) + (self.state.height / 2)

        return screen_x, screen_y

    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates.

        Args:
            screen_x: X coordinate in screen space
            screen_y: Y coordinate in screen space

        Returns:
            Tuple[float, float]: (world_x, world_y)
        """
        # Center screen coordinates
        centered_x = screen_x - (self.state.width / 2)
        centered_y = screen_y - (self.state.height / 2)

        # Apply inverse zoom and add camera position
        world_x = (centered_x / self.state.zoom) + self.state.world_x
        world_y = (centered_y / self.state.zoom) + self.state.world_y

        return world_x, world_y

    def is_in_viewport(self, world_x: float, world_y: float) -> bool:
        """Check if a world coordinate is within the viewport bounds.

        Args:
            world_x: X coordinate in world space
            world_y: Y coordinate in world space

        Returns:
            bool: True if the point is in the viewport
        """
        left, top, right, bottom = self.state.bounds
        return (left <= world_x <= right) and (top <= world_y <= bottom)

    def get_visible_bounds(self) -> Tuple[float, float, float, float]:
        """Get the current viewport bounds in world coordinates.

        Returns:
            Tuple[float, float, float, float]: (left, top, right, bottom)
        """
        return self.state.bounds
