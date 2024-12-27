import pygame
import random
import math
from .person_attributes import PersonAttributes
from typing import Tuple


class Person:
    def __init__(self, x: float, y: float, radius: int = 10):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = (255, 0, 0)  # Default red color
        self.speed = 30
        self.move_target = None
        self.attributes = PersonAttributes()

    def set_random_target(
        self,
        max_x: float,
        max_y: float,
        min_distance: float = 100,
        max_distance: float = 500,
    ):
        """Set a random movement target within bounds"""
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(min_distance, max_distance)
        target_x = self.x + math.cos(angle) * distance
        target_y = self.y + math.sin(angle) * distance

        # Clamp to bounds
        self.move_target = (max(0, min(target_x, max_x)), max(0, min(target_y, max_y)))

    def update(self, delta_time: float):
        """Update person's position"""
        if self.move_target:
            dx = self.move_target[0] - self.x
            dy = self.move_target[1] - self.y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < self.speed:
                self.x = self.move_target[0]
                self.y = self.move_target[1]
                self.move_target = None
            else:
                # Normalize and apply speed
                self.x += (dx / distance) * self.speed * delta_time
                self.y += (dy / distance) * self.speed * delta_time

    def draw(
        self, screen: pygame.Surface, view_x: float, view_y: float, zoom_level: float
    ):
        """Draw person on screen"""
        # Calculate screen position
        screen_x = (self.x - view_x) * zoom_level
        screen_y = (self.y - view_y) * zoom_level

        # Only draw if on screen
        if 0 <= screen_x <= screen.get_width() and 0 <= screen_y <= screen.get_height():
            pygame.draw.circle(
                screen, self.color, (int(screen_x), int(screen_y)), int(self.radius)
            )
