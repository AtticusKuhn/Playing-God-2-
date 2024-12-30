import pygame
from models.person import Person
from models.person_attributes import PersonAttributes

class PersonUI:
    def __init__(self):
        self.visible = True
        self.selected_person = None
        # UI dimensions and position
        self.width = 200
        self.height = 300
        self.padding = 10
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
    def show_person(self, person: Person) -> None:
        """Show UI for a selected person"""
        self.selected_person = person
        self.visible = True
        
    def hide(self):
        """Hide the UI"""
        pass
        # self.visible = False
        # self.selected_person = None
        
    def handle_input(self, event: pygame.event.Event) -> bool:
        """Handle input events"""
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Check if click is outside UI panel
            panel_rect = pygame.Rect(
                self.padding,
                self.padding,
                self.width,
                self.height
            )
            if not panel_rect.collidepoint(mouse_x, mouse_y):
                self.hide()
                return True
                
        return False
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the person UI panel"""
        print(f"[draw] selected_person: {self.selected_person}")
        if not self.selected_person:
            return
            
        # Draw panel background
        panel_rect = pygame.Rect(
            self.padding,
            self.padding,
            self.width,
            self.height
        )
        pygame.draw.rect(screen, (200, 200, 200), panel_rect)
        pygame.draw.rect(screen, (100, 100, 100), panel_rect, 2)
        
        y = self.padding * 2
        
        # Draw person info
        attrs: PersonAttributes = self.selected_person.attributes
        
        # Basic info
        self._draw_text(screen, f"Name: {attrs.name or 'Unknown'}", y)
        y += 30
        self._draw_text(screen, f"Age: {attrs.age}", y)
        y += 40
        
        # Spiritual attributes
        self._draw_text(screen, "Faith:", y)
        y += 20
        faith_width = 180
        faith_rect = pygame.Rect(self.padding + 10, y, faith_width, 10)
        pygame.draw.rect(screen, (50, 50, 50), faith_rect)
        faith_fill = pygame.Rect(
            self.padding + 10,
            y,
            faith_width * attrs.faith,
            10
        )
        pygame.draw.rect(screen, (0, 255, 0), faith_fill)
        y += 40
        
        # Mental attributes
        self._draw_text(screen, "Emotional State:", y)
        y += 20
        emotion_rect = pygame.Rect(self.padding + 10, y, faith_width, 10)
        pygame.draw.rect(screen, (50, 50, 50), emotion_rect)
        emotion_fill = pygame.Rect(
            self.padding + 10,
            y,
            faith_width * attrs.emotional_state,
            10
        )
        pygame.draw.rect(screen, (0, 0, 255), emotion_fill)
        y += 30
        
        self._draw_text(screen, "Life Satisfaction:", y)
        y += 20
        satisfaction_rect = pygame.Rect(self.padding + 10, y, faith_width, 10)
        pygame.draw.rect(screen, (50, 50, 50), satisfaction_rect)
        satisfaction_fill = pygame.Rect(
            self.padding + 10,
            y,
            faith_width * attrs.life_satisfaction,
            10
        )
        pygame.draw.rect(screen, (255, 165, 0), satisfaction_fill)
        y += 40
        
        # Prayer info
        active_prayers = self.selected_person.get_active_prayers()
        self._draw_text(screen, f"Active Prayers: {len(active_prayers)}", y)
        y += 30
        if active_prayers:
            self._draw_text(
                screen,
                f"Latest: {active_prayers[-1].content}",
                y,
                self.small_font,
                wrap_width=180
            )
            
    def _draw_text(
        self,
        screen: pygame.Surface,
        text: str,
        y: int,
        font=None,
        wrap_width=None
    ):
        """Helper to draw text with optional wrapping"""
        if font is None:
            font = self.font
            
        if wrap_width:
            words = text.split()
            lines = []
            current_line = []
            current_width = 0
            
            for word in words:
                word_surface = font.render(word + " ", True, (0, 0, 0))
                word_width = word_surface.get_width()
                
                if current_width + word_width > wrap_width:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    current_width = word_width
                else:
                    current_line.append(word)
                    current_width += word_width
                    
            if current_line:
                lines.append(" ".join(current_line))
                
            for line in lines:
                text_surface = font.render(line, True, (0, 0, 0))
                screen.blit(
                    text_surface,
                    (self.padding * 2, y)
                )
                y += font.get_linesize()
        else:
            text_surface = font.render(text, True, (0, 0, 0))
            screen.blit(
                text_surface,
                (self.padding * 2, y)
            )
