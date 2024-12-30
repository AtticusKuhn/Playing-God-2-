import pygame
import random
import math
from typing import List, Optional
from .person_attributes import PersonAttributes
from .prayer import Prayer


class Person:
    # Custom event for resetting prayer color
    RESET_PRAYER_COLOR_EVENT = pygame.USEREVENT + 1

    def __init__(self, x: float, y: float, radius: int = 4):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = (255, 0, 0)  # Default red color
        self.move_target = None
        # Initialize attributes with random name and age
        self.attributes = PersonAttributes(
            name=self._generate_random_name(), age=random.randint(18, 80)
        )
        self.speed = self.attributes.walking_speed
        self.default_color = (255, 0, 0)  # Store default color

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

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events for this person"""
        if event.type == self.RESET_PRAYER_COLOR_EVENT:
            self.color = self.default_color

    def get_active_prayers(self) -> List[Prayer]:
        """Get all unanswered prayers"""
        return [p for p in self.attributes.prayers if not p.was_answered]

    def handle_prayer_response(self, prayer: Prayer, response_type: str, response: Optional[str]) -> None:
        """Handle a response to a prayer"""
        prayer.answer(response_type, response)

        # Adjust faith based on response
        if response_type == "accepted":
            self.attributes.faith = min(1.0, self.attributes.faith + 0.1)
            self.color = (0, 255, 0)  # Green for accepted prayers
        elif response_type == "denied":
            self.attributes.faith = max(0.0, self.attributes.faith - 0.05)
            self.color = (255, 165, 0)  # Orange for denied prayers
        # Delayed prayers don't affect faith

        # Reset color after 1 second
        pygame.time.set_timer(self.RESET_PRAYER_COLOR_EVENT, 1000, loops=1)

    def update(self, delta_time: float) -> None:
        """Update person's position and generate prayers"""
        # Update movement
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

        # Generate prayer if possible
        prayer = self.attributes.generate_prayer()
        if prayer:
            # Change color temporarily when praying
            self.color = (0, 0, 255)  # Blue
            # Reset color after 1 second
            pygame.time.set_timer(self.RESET_PRAYER_COLOR_EVENT, 1000, loops=1)

    def _generate_random_name(self) -> str:
        """Generate a random name for the person"""
        first_names = [
            "John",
            "Mary",
            "James",
            "Sarah",
            "Michael",
            "Emma",
            "David",
            "Anna",
            "Robert",
            "Lisa",
            "William",
            "Emily",
            "Joseph",
            "Sofia",
            "Thomas",
            "Olivia",
            "Daniel",
            "Isabella",
            "Matthew",
            "Ava",
        ]
        last_names = [
            "Smith",
            "Johnson",
            "Williams",
            "Brown",
            "Jones",
            "Garcia",
            "Miller",
            "Davis",
            "Rodriguez",
            "Martinez",
            "Hernandez",
            "Lopez",
            "Gonzalez",
            "Wilson",
            "Anderson",
            "Thomas",
            "Taylor",
            "Moore",
            "Jackson",
            "Martin",
        ]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

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
