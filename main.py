import pygame
import sys
import asyncio
from map_manager import MapManager
from people import PeopleManager

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
ZOOM_SPEED = 0.01
PAN_SPEED = 10

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("World Map Game")
        self.clock = pygame.time.Clock()

        # Initialize managers
        self.map_manager = MapManager(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.people_manager = PeopleManager(map_width = WINDOW_HEIGHT, map_height = WINDOW_HEIGHT)
        
        # Add some initial people
        self.people_manager.add_random_people(100)

        # Camera/view properties
        self.zoom_level = 1.0
        # Initialize view to London coordinates
        # lon, lat = -0.1278, 51.5074  # London coordinates
        # self.view_x, self.view_y = self.map_manager.lat_lon_to_pixel(lat, lon, 2)
        self.view_x = 0
        self.view_y = 0
        print(f"Initial view position: ({self.view_x}, {self.view_y})")

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Pan with arrow keys
        if keys[pygame.K_LEFT]:
            self.view_x -= PAN_SPEED / self.zoom_level
        if keys[pygame.K_RIGHT]:
            self.view_x += PAN_SPEED / self.zoom_level
        if keys[pygame.K_UP]:
            self.view_y -= PAN_SPEED / self.zoom_level
        if keys[pygame.K_DOWN]:
            self.view_y += PAN_SPEED / self.zoom_level
        if keys[pygame.K_p]:
            self.zoom_level *= 1 + ZOOM_SPEED
        if keys[pygame.K_MINUS]:
            self.zoom_level *= 1 - ZOOM_SPEED
        if keys[pygame.K_EQUALS]:
            self.zoom_level = 1

        # Handle mouse events for zooming
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEWHEEL:
                # Zoom in/out with mouse wheel
                if event.y > 0:  # Scroll up
                    self.zoom_level *= 1 + ZOOM_SPEED
                else:  # Scroll down
                    self.zoom_level *= 1 - ZOOM_SPEED
                # Clamp zoom level
                self.zoom_level = max(0.5, min(self.zoom_level, 5.0))

        return True

    def update(self):
        print(f"Game state - zoom: {self.zoom_level}, pos: ({self.view_x}, {self.view_y})")
        self.map_manager.update(self.view_x, self.view_y, self.zoom_level)
        self.people_manager.update()

    def draw(self):
        self.screen.fill((0, 0, 255))  # Clear screen
        self.map_manager.draw(self.screen)
        self.people_manager.draw(self.screen, self.view_x, self.view_y, self.zoom_level)
        pygame.display.flip()

    async def game_loop(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)
            # Allow other async operations to run
            await asyncio.sleep(0)

        # Cleanup
        self.map_manager.cleanup()
        pygame.quit()

def main():
    # Set up the event loop
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        game = Game()
        loop.run_until_complete(game.game_loop())
    except KeyboardInterrupt:
        print("Game interrupted by user")
    finally:
        loop.close()
        sys.exit()

if __name__ == "__main__":
    main()
