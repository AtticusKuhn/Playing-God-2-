"""Game configuration constants."""

from dataclasses import dataclass


@dataclass
class WindowConfig:
    """Window-related configuration."""

    WIDTH: int = 1024
    HEIGHT: int = 768
    TITLE: str = "Playing God Game"
    FPS: int = 60


@dataclass
class CameraConfig:
    """Camera-related configuration."""

    ZOOM_SPEED: float = 0.01
    PAN_SPEED: float = 10
    MIN_ZOOM: float = 0.5
    MAX_ZOOM: float = 5.0
    INITIAL_ZOOM: float = 1.0


@dataclass
class UIConfig:
    """UI-related configuration."""

    PRAYER_PANEL_WIDTH: int = 300
    PRAYER_ITEM_HEIGHT: int = 70
    MAX_VISIBLE_PRAYERS: int = 5
    FONT_SIZE: int = 24
    OVERLAY_ALPHA: int = 128
