import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
PLAY_AREA_WIDTH = 600
PLAY_AREA_HEIGHT = 600
SIDEBAR_WIDTH = 200
WINDOW_WIDTH = PLAY_AREA_WIDTH + SIDEBAR_WIDTH
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = PLAY_AREA_WIDTH // GRID_SIZE
GRID_HEIGHT = PLAY_AREA_HEIGHT // GRID_SIZE

# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (180, 180, 180)
DARK_GRAY = (50, 50, 50)

# Directions as vectors
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Button:
    """A simple clickable button for the sidebar."""
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.is_hovered = False

    def draw(self, surface, font):
        """Draw the button on the given surface."""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        """Check for hover and click events."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.action:
                self.action()

class ToggleButton(Button):
    """A button that toggles between two states (e.g., ON/OFF)."""
    def __init__(self, x, y, width, height, text, color, hover_color, initial_state=True, action=None):
        super().__init__(x, y, width, height, text, color, hover_color, action)
        self.state = initial_state  # True = ON, False = OFF

    def draw(self, surface, font):
        """Draw with state indicator."""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        # Display text with state
        display_text = f"{self.text}: {'ON' if self.state else 'OFF'}"
        text_surf = font.render(display_text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def toggle(self):
        """Flip the state."""
        self.state = not self.state
        if self.action:
            self.action(self.state)

    def handle_event(self, event):
        """Check hover and toggle on click."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.toggle()

class Snake:
    """Represents the snake: body, direction, growth, and drawing."""
    def __init__(self):
        self.body = [
            (GRID_WIDTH // 2, GRID_HEIGHT // 2),
            (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
            (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)
        ]
        self.direction = RIGHT
        self.grow_flag = False

    def move(self):
        """Move the snake one cell in the current direction."""
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        self.body.insert(0, new_head)
        if not self.grow_flag:
            self.body.pop()
        else:
            self.grow_flag = False

    def grow(self):
        """Signal that the snake should grow on the next move."""
        self.grow_flag = True

    def set_direction(self, new_dir):
        """Prevent 180° turns."""
        if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
            self.direction = new_dir

    def check_self_collision(self):
        """Return True if head collides with body."""
        head = self.body[0]
        return head in self.body[1:]

    def draw(self, surface):
        """Draw the snake. The head is drawn differently (circle with eyes)."""
        for i, segment in enumerate(self.body):
            rect = pygame.Rect(
                segment[0] * GRID_SIZE,
                segment[1] * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE
            )
            if i == 0:  # Head
                # Draw a circle for the head
                center = rect.center
                radius = GRID_SIZE // 2
                pygame.draw.circle(surface, DARK_GREEN, center, radius)
                pygame.draw.circle(surface, BLACK, center, radius, 1)
                # Eyes (direction dependent)
                eye_offset = GRID_SIZE // 4
                if self.direction == RIGHT:
                    left_eye = (center[0] + eye_offset, center[1] - eye_offset)
                    right_eye = (center[0] + eye_offset, center[1] + eye_offset)
                elif self.direction == LEFT:
                    left_eye = (center[0] - eye_offset, center[1] - eye_offset)
                    right_eye = (center[0] - eye_offset, center[1] + eye_offset)
                elif self.direction == UP:
                    left_eye = (center[0] - eye_offset, center[1] - eye_offset)
                    right_eye = (center[0] + eye_offset, center[1] - eye_offset)
                else:  # DOWN
                    left_eye = (center[0] - eye_offset, center[1] + eye_offset)
                    right_eye = (center[0] + eye_offset, center[1] + eye_offset)
                pygame.draw.circle(surface, WHITE, left_eye, 3)
                pygame.draw.circle(surface, WHITE, right_eye, 3)
                pygame.draw.circle(surface, BLACK, left_eye, 1)
                pygame.draw.circle(surface, BLACK, right_eye, 1)
            else:
                pygame.draw.rect(surface, GREEN, rect)
                pygame.draw.rect(surface, BLACK, rect, 1)

class Food:
    """Represents the food item."""
    def __init__(self, snake_body):
        self.position = self.randomize_position(snake_body)

    def randomize_position(self, snake_body):
        """Generate a random grid position not occupied by the snake."""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in snake_body:
                return (x, y)

    def draw(self, surface):
        """Draw the food as a red square with a highlight."""
        rect = pygame.Rect(
            self.position[0] * GRID_SIZE,
            self.position[1] * GRID_SIZE,
            GRID_SIZE,
            GRID_SIZE
        )
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.rect(surface, YELLOW, rect, 2)

class Game:
    """Main game class with sidebar controls."""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game - Enhanced")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)
        self.big_font = pygame.font.SysFont("Arial", 36)

        # Speed options
        self.speed_levels = {"Slow": 200, "Medium": 150, "Fast": 100}
        self.current_speed = "Medium"
        self.move_delay = self.speed_levels[self.current_speed]

        # Wall mode: True = walls kill, False = wrap around
        self.walls_enabled = True

        # Create UI elements
        self.create_sidebar_buttons()

        self.reset_game()

    def create_sidebar_buttons(self):
        """Initialize buttons for the sidebar."""
        btn_width = 160
        btn_height = 40
        start_x = PLAY_AREA_WIDTH + (SIDEBAR_WIDTH - btn_width) // 2
        y = 150
        spacing = 60

        # Speed buttons (three separate buttons for simplicity)
        self.speed_slow_btn = Button(
            start_x, y, btn_width, btn_height, "Slow",
            GRAY, LIGHT_GRAY, action=lambda: self.set_speed("Slow")
        )
        y += spacing
        self.speed_medium_btn = Button(
            start_x, y, btn_width, btn_height, "Medium",
            BLUE, LIGHT_GRAY, action=lambda: self.set_speed("Medium")
        )
        y += spacing
        self.speed_fast_btn = Button(
            start_x, y, btn_width, btn_height, "Fast",
            RED, LIGHT_GRAY, action=lambda: self.set_speed("Fast")
        )
        y += spacing + 20

        # Wall toggle button
        self.wall_toggle_btn = ToggleButton(
            start_x, y, btn_width, btn_height, "Walls",
            GRAY, LIGHT_GRAY, initial_state=True,
            action=lambda state: setattr(self, 'walls_enabled', state)
        )
        y += spacing + 20

        # Restart button
        self.restart_btn = Button(
            start_x, y, btn_width, btn_height, "Restart",
            DARK_GRAY, LIGHT_GRAY, action=self.reset_game
        )

        self.buttons = [
            self.speed_slow_btn, self.speed_medium_btn, self.speed_fast_btn,
            self.wall_toggle_btn, self.restart_btn
        ]

    def set_speed(self, level):
        """Change the movement delay based on selected speed."""
        self.current_speed = level
        self.move_delay = self.speed_levels[level]

    def reset_game(self):
        """Reset game state to start a new game."""
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.score = 0
        self.game_over = False
        self.last_move_time = pygame.time.get_ticks()
        # Reset wall toggle to its current state (doesn't change)

    def handle_events(self):
        """Process input events (keyboard, mouse)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                else:
                    if event.key == pygame.K_UP:
                        self.snake.set_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.set_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.set_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.set_direction(RIGHT)

            # Mouse events for buttons
            for btn in self.buttons:
                btn.handle_event(event)

    def update(self):
        """Update game state: move snake, collisions, food."""
        if self.game_over:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time >= self.move_delay:
            self.snake.move()
            self.last_move_time = current_time

            head_x, head_y = self.snake.body[0]

            # Wall collision or wrap
            if self.walls_enabled:
                if head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT:
                    self.game_over = True
            else:
                # Wrap around
                head_x = head_x % GRID_WIDTH
                head_y = head_y % GRID_HEIGHT
                self.snake.body[0] = (head_x, head_y)

            # Self collision
            if self.snake.check_self_collision():
                self.game_over = True

            # Food collision
            if self.snake.body[0] == self.food.position:
                self.snake.grow()
                self.score += 1
                self.food = Food(self.snake.body)

    def draw_grid(self):
        """Draw grid lines on the play area."""
        for x in range(0, PLAY_AREA_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (x, 0), (x, PLAY_AREA_HEIGHT))
        for y in range(0, PLAY_AREA_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (0, y), (PLAY_AREA_WIDTH, y))

    def draw_sidebar(self):
        """Draw the control panel on the right side."""
        # Sidebar background
        sidebar_rect = pygame.Rect(PLAY_AREA_WIDTH, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, (30, 30, 30), sidebar_rect)

        # Title
        title = self.big_font.render("Controls", True, WHITE)
        title_rect = title.get_rect(center=(PLAY_AREA_WIDTH + SIDEBAR_WIDTH//2, 40))
        self.screen.blit(title, title_rect)

        # Score display
        score_text = self.font.render(f"Score: {self.score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(PLAY_AREA_WIDTH + SIDEBAR_WIDTH//2, 90))
        self.screen.blit(score_text, score_rect)

        # Current speed indicator
        speed_text = self.font.render(f"Speed: {self.current_speed}", True, WHITE)
        speed_rect = speed_text.get_rect(center=(PLAY_AREA_WIDTH + SIDEBAR_WIDTH//2, 120))
        self.screen.blit(speed_text, speed_rect)

        # Draw buttons
        for btn in self.buttons:
            btn.draw(self.screen, self.font)

        # Instruction
        instr = self.font.render("Arrow keys to move", True, LIGHT_GRAY)
        instr_rect = instr.get_rect(center=(PLAY_AREA_WIDTH + SIDEBAR_WIDTH//2, 500))
        self.screen.blit(instr, instr_rect)

    def draw_game_over(self):
        """Display game over overlay on the play area."""
        overlay = pygame.Surface((PLAY_AREA_WIDTH, PLAY_AREA_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        go_text = self.big_font.render("GAME OVER", True, RED)
        go_rect = go_text.get_rect(center=(PLAY_AREA_WIDTH//2, PLAY_AREA_HEIGHT//2 - 30))
        self.screen.blit(go_text, go_rect)

        restart_text = self.font.render("Press R or click Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(PLAY_AREA_WIDTH//2, PLAY_AREA_HEIGHT//2 + 20))
        self.screen.blit(restart_text, restart_rect)

    def draw(self):
        """Render everything."""
        self.screen.fill(BLACK)
        # Play area
        self.draw_grid()
        self.snake.draw(self.screen)
        self.food.draw(self.screen)

        if self.game_over:
            self.draw_game_over()

        # Sidebar
        self.draw_sidebar()

        # Border between play area and sidebar
        pygame.draw.line(self.screen, WHITE, (PLAY_AREA_WIDTH, 0), (PLAY_AREA_WIDTH, WINDOW_HEIGHT), 2)

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)


if __name__ == "__main__":
    game = Game()
    game.run()