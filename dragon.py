import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)

# Physics constants
GRAVITY = 0.5
FLAP_FORCE = -8.0  # Upward impulse

# Game settings
DRAGON_START_X = 150
DRAGON_START_Y = SCREEN_HEIGHT // 2
OBSTACLE_WIDTH = 60
OBSTACLE_GAP = 200
OBSTACLE_SPEED = 5
OBSTACLE_SPAWN_INTERVAL = 120  # frames
GROUND_HEIGHT = 50

# Difficulty scaling
SPEED_INCREMENT = 0.1
SPEED_INCREMENT_INTERVAL = 500  # frames


class Dragon:
    """Handles dragon physics, position, and drawing."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0.0
        self.width = 40
        self.height = 30
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        # For simple animation
        self.wing_up = True
        self.animation_counter = 0

    def flap(self):
        """Apply upward impulse."""
        self.velocity = FLAP_FORCE

    def update(self):
        """Apply gravity and update position."""
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = int(self.y)
        self.rect.x = self.x  # x is fixed

        # Simple wing flap animation toggle (for visual effect)
        self.animation_counter += 1
        if self.animation_counter > 5:
            self.wing_up = not self.wing_up
            self.animation_counter = 0

    def draw(self, screen):
        """Draw the dragon as a simple shape with wing indication."""
        # Body
        pygame.draw.ellipse(screen, GREEN, self.rect)
        # Wing (simple triangle)
        wing_x = self.rect.right - 10
        wing_y = self.rect.centery
        if self.wing_up:
            points = [(wing_x, wing_y), (wing_x + 20, wing_y - 15), (wing_x + 20, wing_y + 5)]
        else:
            points = [(wing_x, wing_y), (wing_x + 20, wing_y - 5), (wing_x + 20, wing_y + 15)]
        pygame.draw.polygon(screen, (0, 150, 0), points)
        # Eye
        pygame.draw.circle(screen, BLACK, (self.rect.right - 8, self.rect.centery - 5), 4)

    def get_rect(self):
        return self.rect


class Obstacle:
    """Represents a pair of pillars (top and bottom) with a gap."""
    def __init__(self, x, gap_y, gap_size):
        self.x = x
        self.gap_y = gap_y
        self.gap_size = gap_size
        self.width = OBSTACLE_WIDTH
        self.passed = False  # For scoring

        # Top pillar
        self.top_rect = pygame.Rect(self.x, 0, self.width, gap_y)
        # Bottom pillar
        bottom_height = SCREEN_HEIGHT - GROUND_HEIGHT - (gap_y + gap_size)
        self.bottom_rect = pygame.Rect(self.x, gap_y + gap_size, self.width, bottom_height)

    def update(self, speed):
        """Move obstacle left by current speed."""
        self.x -= speed
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, screen):
        """Draw both pillars."""
        pygame.draw.rect(screen, RED, self.top_rect)
        pygame.draw.rect(screen, RED, self.bottom_rect)

    def off_screen(self):
        """Check if obstacle is completely off the left side."""
        return self.x + self.width < 0

    def get_rects(self):
        """Return both pillar rects for collision."""
        return [self.top_rect, self.bottom_rect]


class Game:
    """Main game manager."""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flying Dragon")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

        # Background scrolling
        self.bg_x = 0
        self.bg_speed = 2

        self.reset_game()

    def reset_game(self):
        """Reset all game variables for a new game."""
        self.dragon = Dragon(DRAGON_START_X, DRAGON_START_Y)
        self.obstacles = []
        self.score = 0
        self.game_active = False
        self.game_over = False

        # Difficulty variables
        self.current_speed = OBSTACLE_SPEED
        self.frame_count = 0
        self.spawn_timer = 0

    def spawn_obstacle(self):
        """Create a new obstacle at the right edge with random gap position."""
        gap_y = random.randint(100, SCREEN_HEIGHT - GROUND_HEIGHT - OBSTACLE_GAP - 50)
        new_obstacle = Obstacle(SCREEN_WIDTH, gap_y, OBSTACLE_GAP)
        self.obstacles.append(new_obstacle)

    def check_collisions(self):
        """Check dragon collision with ground, ceiling, or any obstacle."""
        # Ground collision
        if self.dragon.rect.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT:
            return True
        # Ceiling collision
        if self.dragon.rect.top <= 0:
            return True

        # Obstacle collisions
        dragon_rect = self.dragon.get_rect()
        for obs in self.obstacles:
            for rect in obs.get_rects():
                if dragon_rect.colliderect(rect):
                    return True
        return False

    def update_score(self):
        """Increase score when dragon passes an obstacle."""
        dragon_x = self.dragon.x
        for obs in self.obstacles:
            if not obs.passed and obs.x + obs.width < dragon_x:
                obs.passed = True
                self.score += 1

    def handle_events(self):
        """Process user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if self.game_active:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        self.dragon.flap()
                elif self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.game_active = True
                        self.game_over = False
                else:  # Start screen
                    if event.key == pygame.K_SPACE:
                        self.game_active = True
                        self.game_over = False

    def update(self):
        """Update all game objects and logic."""
        if not self.game_active:
            return

        # Update dragon physics
        self.dragon.update()

        # Increase difficulty over time
        self.frame_count += 1
        if self.frame_count % SPEED_INCREMENT_INTERVAL == 0:
            self.current_speed += SPEED_INCREMENT

        # Spawn new obstacles
        self.spawn_timer += 1
        if self.spawn_timer >= OBSTACLE_SPAWN_INTERVAL:
            self.spawn_obstacle()
            self.spawn_timer = 0

        # Update obstacles and remove off-screen ones
        for obs in self.obstacles[:]:
            obs.update(self.current_speed)
            if obs.off_screen():
                self.obstacles.remove(obs)

        # Update score (based on passing obstacles)
        self.update_score()

        # Collision detection
        if self.check_collisions():
            self.game_active = False
            self.game_over = True

        # Scroll background
        self.bg_x -= self.bg_speed
        if self.bg_x <= -SCREEN_WIDTH:
            self.bg_x = 0

    def draw_background(self):
        """Draw scrolling background (simple gradient with clouds)."""
        # Sky gradient
        for y in range(SCREEN_HEIGHT):
            color_value = 135 + int(120 * y / SCREEN_HEIGHT)
            color = (color_value, 206, 235)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

        # Scrolling clouds (simple circles)
        cloud_color = (255, 255, 255)
        for i in range(3):
            cloud_x = (self.bg_x + i * 300) % (SCREEN_WIDTH + 200) - 100
            pygame.draw.ellipse(self.screen, cloud_color, (cloud_x, 80, 100, 40))
            pygame.draw.ellipse(self.screen, cloud_color, (cloud_x + 30, 60, 80, 30))
            pygame.draw.ellipse(self.screen, cloud_color, (cloud_x - 20, 90, 80, 30))

        # Ground
        pygame.draw.rect(self.screen, (34, 139, 34), (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        pygame.draw.rect(self.screen, (0, 100, 0), (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, 5))

    def draw_ui(self):
        """Draw score and messages."""
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Speed indicator
        speed_text = self.font.render(f"Speed: {self.current_speed:.1f}", True, WHITE)
        self.screen.blit(speed_text, (SCREEN_WIDTH - 150, 10))

        if not self.game_active and not self.game_over:
            # Start screen
            title = self.big_font.render("FLYING DRAGON", True, YELLOW)
            prompt = self.font.render("Press SPACE to Start", True, WHITE)
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 80))
            self.screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT//2))

        if self.game_over:
            # Game over screen
            over_text = self.big_font.render("GAME OVER", True, RED)
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.font.render("Press R to Restart", True, WHITE)
            self.screen.blit(over_text, (SCREEN_WIDTH//2 - over_text.get_width()//2, SCREEN_HEIGHT//2 - 80))
            self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 50))

    def draw(self):
        """Render all elements."""
        self.draw_background()

        # Draw obstacles
        for obs in self.obstacles:
            obs.draw(self.screen)

        # Draw dragon
        self.dragon.draw(self.screen)

        # Draw UI
        self.draw_ui()

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()