import pygame
import random
from typing import List
from models.person import Person


class PeopleManager:
    def __init__(self, map_width: float = 10000, map_height: float = 10000):
        self.people: List[Person] = []
        self.map_width = map_width
        self.map_height = map_height
        self.last_update = pygame.time.get_ticks()

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

    def update(self):
        """Update all people"""
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - self.last_update) / 1000.0  # Convert to seconds
        self.last_update = current_time

        for person in self.people:
            person.update(delta_time)
            # If person has no target, set a new random target
            if not person.move_target:
                person.set_random_target(self.map_width, self.map_height)

    def draw(
        self, screen: pygame.Surface, view_x: float, view_y: float, zoom_level: float
    ):
        """Draw all people"""
        for person in self.people:
            person.draw(screen, view_x, view_y, zoom_level)
