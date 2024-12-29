import pygame
import random
from typing import List, Optional, Dict
from models.person import Person
from models.prayer import Prayer


class PeopleManager:
    # Custom event for prayer inbox updates
    PRAYER_RECEIVED_EVENT = pygame.USEREVENT + 2

    def __init__(self, map_width: float = 10000, map_height: float = 10000):
        self.people: List[Person] = []
        self.map_width = map_width
        self.map_height = map_height
        self.last_update = pygame.time.get_ticks()
        # Track all active prayers for easy access
        self.active_prayers: Dict[int, tuple[Person, Prayer]] = {}
        self._next_prayer_id = 1

    def add_random_people(self, count: int):
        """Add multiple people at random positions"""
        for _ in range(count):
            person = Person(
                x=random.uniform(0, self.map_width),
                y=random.uniform(0, self.map_height),
            )
            self.people.append(person)
            # Set initial movement target
            person.set_random_target(self.map_width, self.map_height)

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events"""
        # Forward events to all people
        for person in self.people:
            person.handle_event(event)

    def get_prayer(self, prayer_id: int) -> Optional[tuple[Person, Prayer]]:
        """Get a prayer and its person by ID"""
        return self.active_prayers.get(prayer_id)

    def answer_prayer(self, prayer_id: int, response_type: str):
        """Answer a prayer with accept/deny/delay"""
        if prayer_pair := self.active_prayers.get(prayer_id):
            person, prayer = prayer_pair
            person.handle_prayer_response(prayer, response_type)
            # Remove from active prayers if not delayed
            if response_type != "delayed":
                del self.active_prayers[prayer_id]

    def update(self):
        """Update all people and manage prayers"""
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - self.last_update) / 1000.0  # Convert to seconds
        self.last_update = current_time

        for person in self.people:
            person.update(delta_time)
            # Check for new prayers
            for prayer in person.get_active_prayers():
                # Only add prayers that aren't already tracked
                if prayer not in [p for _, p in self.active_prayers.values()]:
                    prayer_id = self._next_prayer_id
                    self._next_prayer_id += 1
                    self.active_prayers[prayer_id] = (person, prayer)
                    # Post event for new prayer
                    pygame.event.post(
                        pygame.event.Event(
                            self.PRAYER_RECEIVED_EVENT, {"prayer_id": prayer_id}
                        )
                    )

            # If person has no target, set a new random target
            if not person.move_target:
                person.set_random_target(self.map_width, self.map_height)

    def draw(
        self, screen: pygame.Surface, view_x: float, view_y: float, zoom_level: float
    ):
        """Draw all people"""
        for person in self.people:
            person.draw(screen, view_x, view_y, zoom_level)
