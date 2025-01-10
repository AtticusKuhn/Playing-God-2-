"""Camera manager for handling view and zoom functionality."""

from dataclasses import dataclass
import pygame
from config import CameraConfig


@dataclass
class CameraState:
    """Represents the current state of the camera."""

    x: float = 0
    y: float = 0
    zoom: float = CameraConfig.INITIAL_ZOOM


class CameraManager:
    """Manages camera position and zoom level."""

    def __init__(self):
        """Initialize the camera manager."""
        self.state = CameraState()

    def handle_input(self, keys, events: list[pygame.event.Event]) -> None:
        """Handle camera input events."""
        # Handle keyboard input for panning
        if keys[pygame.K_LEFT]:
            self.state.x -= CameraConfig.PAN_SPEED / self.state.zoom
        if keys[pygame.K_RIGHT]:
            self.state.x += CameraConfig.PAN_SPEED / self.state.zoom
        if keys[pygame.K_UP]:
            self.state.y -= CameraConfig.PAN_SPEED / self.state.zoom
        if keys[pygame.K_DOWN]:
            self.state.y += CameraConfig.PAN_SPEED / self.state.zoom

        # Handle keyboard input for zoom
        if keys[pygame.K_p]:
            self._adjust_zoom(1 + CameraConfig.ZOOM_SPEED)
        if keys[pygame.K_MINUS]:
            self._adjust_zoom(1 - CameraConfig.ZOOM_SPEED)
        if keys[pygame.K_EQUALS]:
            self.state.zoom = CameraConfig.INITIAL_ZOOM

        # Handle mouse wheel for zoom
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:  # Scroll up
                    self._adjust_zoom(1 + CameraConfig.ZOOM_SPEED)
                else:  # Scroll down
                    self._adjust_zoom(1 - CameraConfig.ZOOM_SPEED)

    def _adjust_zoom(self, factor: float) -> None:
        """Adjust zoom level by a factor, keeping it within bounds."""
        new_zoom = self.state.zoom * factor
        self.state.zoom = new_zoom
        # self.state.zoom = max(
        #     CameraConfig.MIN_ZOOM, min(new_zoom, CameraConfig.MAX_ZOOM)
        # )

    def get_transform_params(self) -> tuple[float, float, float]:
        """Get the current transform parameters for rendering.

        Returns:
            tuple[float, float, float]: (view_x, view_y, zoom_level)
        """
        return self.state.x, self.state.y, self.state.zoom
