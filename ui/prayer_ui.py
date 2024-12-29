"""Prayer UI component."""

import pygame
from typing import Dict, Optional, Tuple
from config import UIConfig, WindowConfig
from models.prayer import Prayer
from models.person import Person


class PrayerUI:
    """Handles the prayer interface overlay."""

    def __init__(self):
        """Initialize the prayer UI component."""
        self.visible = False
        self.selected_prayer_id: Optional[int] = None
        self.scroll_position = 0
        self.font = pygame.font.Font(None, UIConfig.FONT_SIZE)

        # Create the overlay surface once
        self.overlay = pygame.Surface(
            (UIConfig.PRAYER_PANEL_WIDTH, WindowConfig.HEIGHT)
        )
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(UIConfig.OVERLAY_ALPHA)

    def toggle_visibility(self) -> None:
        """Toggle the visibility of the prayer UI."""
        self.visible = not self.visible

    def handle_input(
        self,
        event: pygame.event.Event,
        active_prayers: Dict[int, Tuple[Person, Prayer]],
    ) -> Optional[Tuple[int, str]]:
        """Handle input events for the prayer UI.

        Returns:
            Optional[Tuple[int, str]]: (prayer_id, response_type) if a prayer was answered, None otherwise
        """
        if not self.visible:
            return None

        if event.type == pygame.MOUSEWHEEL:
            max_scroll = max(0, len(active_prayers) - UIConfig.MAX_VISIBLE_PRAYERS)
            self.scroll_position = max(
                0, min(max_scroll, self.scroll_position - event.y)
            )
            return None

        if event.type == pygame.KEYDOWN and self.selected_prayer_id is not None:
            if event.key == pygame.K_y:
                return (self.selected_prayer_id, "accepted")
            elif event.key == pygame.K_n:
                return (self.selected_prayer_id, "denied")
            elif event.key == pygame.K_d:
                return (self.selected_prayer_id, "delayed")

        return None

    def show_prayer(self, prayer_id: int) -> None:
        """Show a specific prayer."""
        self.visible = True
        self.selected_prayer_id = prayer_id

    def draw(
        self, screen: pygame.Surface, active_prayers: Dict[int, Tuple[Person, Prayer]]
    ) -> None:
        """Draw the prayer UI overlay."""
        if not self.visible:
            return

        # Draw semi-transparent background
        screen.blit(self.overlay, (WindowConfig.WIDTH - UIConfig.PRAYER_PANEL_WIDTH, 0))

        # Draw prayer list
        y = 10
        visible_prayers = list(active_prayers.items())[self.scroll_position :]

        for prayer_id, (person, prayer) in visible_prayers:
            if y > WindowConfig.HEIGHT - 60:  # Leave space for controls
                break

            # Highlight selected prayer
            if prayer_id == self.selected_prayer_id:
                pygame.draw.rect(
                    screen,
                    (100, 100, 100),
                    (
                        WindowConfig.WIDTH - UIConfig.PRAYER_PANEL_WIDTH + 5,
                        y - 5,
                        UIConfig.PRAYER_PANEL_WIDTH - 10,
                        60,
                    ),
                )

            # Draw prayer content
            text = self.font.render(
                f"Prayer: {prayer.content[:30]}...", True, (255, 255, 255)
            )
            screen.blit(
                text, (WindowConfig.WIDTH - UIConfig.PRAYER_PANEL_WIDTH + 10, y)
            )

            # Draw urgency
            urgency_text = self.font.render(
                f"Urgency: {prayer.urgency:.1f}", True, (255, 255, 255)
            )
            screen.blit(
                urgency_text,
                (WindowConfig.WIDTH - UIConfig.PRAYER_PANEL_WIDTH + 10, y + 20),
            )

            y += UIConfig.PRAYER_ITEM_HEIGHT

        # Draw controls if a prayer is selected
        if self.selected_prayer_id is not None:
            controls = ["[Y] Accept", "[N] Deny", "[D] Delay"]
            y = WindowConfig.HEIGHT - 30
            for i, control in enumerate(controls):
                text = self.font.render(control, True, (255, 255, 255))
                screen.blit(
                    text,
                    (
                        WindowConfig.WIDTH - UIConfig.PRAYER_PANEL_WIDTH + 10 + i * 100,
                        y,
                    ),
                )
