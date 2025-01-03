"""Main game module."""

import sys
import asyncio
import pygame

from config import WindowConfig
from map_manager import MapManager
from managers.people_manager import PeopleManager
from managers.camera_manager import CameraManager
from ui.prayer_ui import PrayerUI
from ui.person_ui import PersonUI
from coordinates import CoordinateManager
from managers.viewport_manager import ViewportManager


class Game:
    """Main game class managing the game loop and components."""

    def __init__(self):
        """Initialize the game and its components."""
        try:
            # Initialize Pygame
            if not pygame.get_init():
                pygame.init()

            # Set up display
            self.screen = pygame.display.set_mode(
                (WindowConfig.WIDTH, WindowConfig.HEIGHT)
            )
            pygame.display.set_caption(WindowConfig.TITLE)
            self.clock = pygame.time.Clock()

            # Initialize managers
            self.camera = CameraManager()
            self.viewport = ViewportManager(WindowConfig.WIDTH, WindowConfig.HEIGHT)
            self.map_manager = MapManager(WindowConfig.WIDTH, WindowConfig.HEIGHT)
            self.people_manager = PeopleManager(
                map_width=WindowConfig.HEIGHT,
                map_height=WindowConfig.HEIGHT,
                viewport=self.viewport
            )
            self.prayer_ui = PrayerUI()
            self.person_ui = PersonUI()

            # Add initial population
            self.people_manager.add_random_people(100)

        except pygame.error as e:
            print(f"Failed to initialize game: {e}")
            raise

    def handle_input(self) -> bool:
        """Handle input events.

        Returns:
            bool: False if the game should exit, True otherwise
        """
        events = pygame.event.get()
        keys = pygame.key.get_pressed()

        for event in events:
            if event.type == pygame.QUIT:
                return False

            # Handle prayer-related events
            if event.type == self.people_manager.PRAYER_RECEIVED_EVENT:
                self.prayer_ui.show_prayer(event.prayer_id)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                self.prayer_ui.toggle_visibility()

            # Update viewport with camera transform
            view_x, view_y, zoom = self.camera.get_transform_params()
            self.viewport.update(view_x, view_y, zoom)

            # Forward events to people manager and check for clicked person
            clicked_person = self.people_manager.handle_event(event)
            if clicked_person is not None:
                self.person_ui.show_person(clicked_person)
            # Handle person UI input
            self.person_ui.handle_input(event)

            # Handle prayer UI input
            if prayer_response := self.prayer_ui.handle_input(
                event, self.people_manager.active_prayers
            ):
                prayer_id, response_type = prayer_response
                self.people_manager.answer_prayer(prayer_id, response_type)
                self.prayer_ui.selected_prayer_id = None

        # Handle camera input when prayer UI is not visible
        if not self.prayer_ui.visible:
            self.camera.handle_input(keys, events)

        return True

    def update(self) -> None:
        """Update game state."""
        try:
            # Update viewport with latest camera transform
            view_x, view_y, zoom = self.camera.get_transform_params()
            self.viewport.update(view_x, view_y, zoom)
            self.map_manager.update()
            self.people_manager.update()
        except Exception as e:
            print(f"Error updating game state: {e}")

    def draw(self) -> None:
        """Draw the game state."""
        try:
            # Clear screen
            self.screen.fill((0, 0, 255))

            # Draw game elements
            self.map_manager.draw(self.screen, self.viewport)
            self.people_manager.draw(self.screen)
            self.prayer_ui.draw(self.screen, self.people_manager.active_prayers)
            self.person_ui.draw(self.screen)

            # Update display
            pygame.display.flip()
        except pygame.error as e:
            print(f"Error drawing game state: {e}")

    async def game_loop(self) -> None:
        """Main game loop."""
        running = True
        while running:
            try:
                running = self.handle_input()
                self.update()
                self.draw()
                self.clock.tick(WindowConfig.FPS)
                await asyncio.sleep(0)  # Allow other async operations to run
            except Exception as e:
                print(f"Error in game loop: {e}")
                running = False

        # Cleanup
        self.cleanup()

    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            self.map_manager.cleanup()
            pygame.quit()
        except Exception as e:
            print(f"Error during cleanup: {e}")


def main() -> None:
    """Entry point for the game."""
    # Set up the event loop policy for Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Create and run event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        game = Game()
        loop.run_until_complete(game.game_loop())
    except KeyboardInterrupt:
        print("Game interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        loop.close()
        sys.exit()


if __name__ == "__main__":
    main()
