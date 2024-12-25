import pygame
import random
import math
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class PersonAttributes:
    """Extensible container for person attributes"""
    # Basic attributes - more can be added later
    name: str = ""
    age: int = 0
    # Add more attributes here as needed

class Person:
    def __init__(self, x: float, y: float, radius: int = 5):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = (255, 0, 0)  # Default red color
        self.speed = 1.0
        self.move_target = None
        self.attributes = PersonAttributes()
        
    def set_random_target(self, max_x: float, max_y: float, min_distance: float = 100, max_distance: float = 500):
        """Set a random movement target within bounds"""
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(min_distance, max_distance)
        target_x = self.x + math.cos(angle) * distance
        target_y = self.y + math.sin(angle) * distance
        
        # Clamp to bounds
        self.move_target = (
            max(0, min(target_x, max_x)),
            max(0, min(target_y, max_y))
        )
    
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

    def draw(self, screen: pygame.Surface, view_x: float, view_y: float, zoom_level: float):
        """Draw person on screen"""
        # Calculate screen position
        screen_x = (self.x - view_x) * zoom_level + screen.get_width() / 2
        screen_y = (self.y - view_y) * zoom_level + screen.get_height() / 2
        
        # Only draw if on screen
        if (0 <= screen_x <= screen.get_width() and 
            0 <= screen_y <= screen.get_height()):
            pygame.draw.circle(
                screen,
                self.color,
                (int(screen_x), int(screen_y)),
                int(self.radius)
            )

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
                y=random.uniform(0, self.map_height)
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
    
    def draw(self, screen: pygame.Surface, view_x: float, view_y: float, zoom_level: float):
        """Draw all people"""
        for person in self.people:
            person.draw(screen, view_x, view_y, zoom_level)
