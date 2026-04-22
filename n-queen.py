"""
Dragon Runner - Enhanced Forest Edition
- Trees of random sizes (width, height, foliage shape)
- Detailed background with mountains and clouds
- Ground texture and parallax scrolling
- Dragon with animated wings and tail
"""

import pygame
import random
import sys

pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (144, 238, 144)
BROWN = (101, 67, 33)
DARK_BROWN = (80, 50, 20)
SKY_BLUE = (135, 206, 235)
MOUNTAIN_COLOR = (100, 100, 120)
CLOUD_COLOR = (255, 255, 255, 180)
GROUND_COLOR = (34, 139, 34)
GROUND_TOP_COLOR = (50, 180, 50)
RED = (200, 0, 0)

# Physics
GRAVITY = 0.8
JUMP_FORCE = -15.0
GROUND_Y = SCREEN_HEIGHT - 50

# Dragon
DRAGON_WIDTH = 30
DRAGON_HEIGHT = 40
DRAGON_X = 100

# Obstacle base settings
BASE_TREE_WIDTH = 35
BASE_TREE_HEIGHT = 55
OBSTACLE_SPEED = 8
OBSTACLE_SPAWN_INTERVAL = 60
SPEED_INCREMENT = 0.2
SPEED_INCREMENT_INTERVAL = 250


class Dragon:
    def __init__(self, x, ground_y):
        self.x = x
        self.ground_y = ground_y - DRAGON_HEIGHT
        self.y = self.ground_y
        self.velocity = 0.0
        self.width = DRAGON_WIDTH
        self.height = DRAGON_HEIGHT
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.is_on_ground = True

        # Animation
        self.leg_phase = 0
        self.wing_phase = 0
        self.animation_speed = 0.15

    def jump(self):
        if self.is_on_ground:
            self.velocity = JUMP_FORCE
            self.is_on_ground = False

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        if self.y >= self.ground_y:
            self.y = self.ground_y
            self.velocity = 0
            self.is_on_ground = True
        self.rect.y = int(self.y)
        self.rect.x = self.x

        if self.is_on_ground:
            self.leg_phase += self.animation_speed
            self.wing_phase += 0.1
        else:
            self.leg_phase = 0
            self.wing_phase += 0.2  # Wings flap faster in air

    def draw(self, screen):
        # Body
        pygame.draw.ellipse(screen, GREEN, self.rect)
        pygame.draw.ellipse(screen, DARK_GREEN, self.rect, 2)

        # Eye
        eye_x = self.rect.right - 8
        eye_y = self.rect.top + 10
        pygame.draw.circle(screen, BLACK, (eye_x, eye_y), 4)
        pygame.draw.circle(screen, WHITE, (eye_x-1, eye_y-1), 1)

        # Horns
        horn1 = (self.rect.left + 5, self.rect.top - 3)
        horn2 = (self.rect.left + 15, self.rect.top - 8)
        pygame.draw.polygon(screen, (200, 150, 0), [horn1, (horn1[0]-3, horn1[1]-10), (horn1[0]+3, horn1[1]-10)])
        pygame.draw.polygon(screen, (200, 150, 0), [horn2, (horn2[0]-3, horn2[1]-10), (horn2[0]+3, horn2[1]-10)])

        # Wings (animated)
        wing_flap = abs(self.wing_phase % 2 - 1) * 15
        wing_base_x = self.rect.centerx
        wing_base_y = self.rect.centery
        wing_tip = (wing_base_x + 20, wing_base_y - 10 - wing_flap)
        pygame.draw.polygon(screen, (0, 150, 0), [(wing_base_x, wing_base_y), wing_tip, (wing_base_x+10, wing_base_y)])

        # Tail (animated with movement)
        tail_offset = int(abs(self.leg_phase % 2 - 1) * 5)
        tail_start = (self.rect.left, self.rect.bottom - 10)
        tail_end = (self.rect.left - 15 - tail_offset, self.rect.bottom - 15)
        pygame.draw.line(screen, DARK_GREEN, tail_start, tail_end, 6)

        # Legs
        leg_offset = int(abs(self.leg_phase % 2 - 1) * 8)
        pygame.draw.line(screen, DARK_GREEN,
                         (self.rect.left + 8, self.rect.bottom),
                         (self.rect.left + 8 - leg_offset, self.rect.bottom + 10), 5)
        pygame.draw.line(screen, DARK_GREEN,
                         (self.rect.right - 8, self.rect.bottom),
                         (self.rect.right - 8 + leg_offset, self.rect.bottom + 10), 5)

    def get_rect(self):
        return self.rect


class TreeObstacle:
    """Tree with random size and shape variations."""
    def __init__(self, x, ground_y):
        self.x = x
        # Random size multiplier (0.8 to 1.5)
        self.size_factor = random.uniform(0.8, 1.5)
        self.width = int(BASE_TREE_WIDTH * self.size_factor)
        self.height = int(BASE_TREE_HEIGHT * self.size_factor)
        self.ground_y = ground_y - self.height
        self.rect = pygame.Rect(self.x, self.ground_y, self.width, self.height)
        self.passed = False

        # Random tree type (affects foliage)
        self.tree_type = random.choice(['pine', 'oak', 'bushy'])

    def update(self, speed):
        self.x -= speed
        self.rect.x = self.x

    def draw(self, screen):
        # Trunk (proportional to size)
        trunk_width = max(6, int(self.width * 0.3))
        trunk_height = int(self.height * 0.5)
        trunk_x = self.x + (self.width - trunk_width) // 2
        trunk_y = self.ground_y + self.height - trunk_height
        pygame.draw.rect(screen, BROWN, (trunk_x, trunk_y, trunk_width, trunk_height))
        # Trunk texture lines
        for i in range(2):
            line_y = trunk_y + 5 + i*8
            pygame.draw.line(screen, DARK_BROWN, (trunk_x+2, line_y), (trunk_x+trunk_width-2, line_y), 1)

        # Foliage (varies by type)
        center_x = self.x + self.width // 2
        base_y = trunk_y - 5

        if self.tree_type == 'pine':
            # Triangle pine tree
            points = [
                (center_x, base_y - int(35 * self.size_factor)),
                (center_x - int(20 * self.size_factor), base_y),
                (center_x + int(20 * self.size_factor), base_y)
            ]
            pygame.draw.polygon(screen, DARK_GREEN, points)
            pygame.draw.polygon(screen, GREEN, points, 2)
        elif self.tree_type == 'oak':
            # Round oak tree
            pygame.draw.circle(screen, DARK_GREEN, (center_x, base_y - 15), int(18 * self.size_factor))
            pygame.draw.circle(screen, GREEN, (center_x - 8, base_y - 25), int(14 * self.size_factor))
            pygame.draw.circle(screen, GREEN, (center_x + 8, base_y - 25), int(14 * self.size_factor))
            pygame.draw.circle(screen, LIGHT_GREEN, (center_x, base_y - 35), int(12 * self.size_factor))
        else:  # bushy
            for i in range(3):
                offset_x = random.randint(-5, 5)  # fixed per instance? we want consistency per tree
                # Use deterministic based on x to keep same shape each frame
                offset_x = int((self.x * 0.1) % 10 - 5)
                pygame.draw.circle(screen, (34, 139, 34),
                                   (center_x + offset_x, base_y - 10 - i*8),
                                   int(12 * self.size_factor))
            pygame.draw.circle(screen, LIGHT_GREEN, (center_x, base_y - 30), int(10 * self.size_factor))

    def off_screen(self):
        return self.x + self.width < 0

    def get_rect(self):
        return self.rect


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dragon Runner - Enchanted Forest")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

        # Parallax background layers
        self.bg_mountains = []
        self.bg_clouds = []
        self.generate_background()

        self.reset_game()

    def generate_background(self):
        # Mountains (static but with scrolling offset)
        self.mountain_points = []
        for i in range(4):
            x = i * 250
            height = random.randint(80, 150)
            points = [(x, GROUND_Y), (x+80, GROUND_Y-height), (x+160, GROUND_Y)]
            self.mountain_points.append(points)

        # Clouds (moving slowly)
        self.clouds = []
        for i in range(5):
            self.clouds.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(30, 120),
                'speed': random.uniform(0.5, 1.2),
                'size': random.randint(40, 80)
            })

    def reset_game(self):
        self.dragon = Dragon(DRAGON_X, GROUND_Y)
        self.obstacles = []
        self.score = 0
        self.game_active = False
        self.game_over = False

        self.current_speed = OBSTACLE_SPEED
        self.frame_count = 0
        self.spawn_timer = 0
        self.scroll_offset = 0

    def spawn_obstacle(self):
        # 80% chance to spawn a tree
        if random.random() < 0.8:
            new_obs = TreeObstacle(SCREEN_WIDTH, GROUND_Y)
            self.obstacles.append(new_obs)

    def check_collisions(self):
        dragon_rect = self.dragon.get_rect()
        for obs in self.obstacles:
            if dragon_rect.colliderect(obs.get_rect()):
                return True
        return False

    def update_score(self):
        dragon_x = self.dragon.x
        for obs in self.obstacles:
            if not obs.passed and obs.x + obs.width < dragon_x:
                obs.passed = True
                self.score += 1

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.game_active:
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        self.dragon.jump()
                elif self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.game_active = True
                        self.game_over = False
                else:
                    if event.key == pygame.K_SPACE:
                        self.game_active = True
                        self.game_over = False

    def update(self):
        if not self.game_active:
            return

        self.dragon.update()

        self.frame_count += 1
        if self.frame_count % SPEED_INCREMENT_INTERVAL == 0:
            self.current_speed += SPEED_INCREMENT

        self.spawn_timer += 1
        if self.spawn_timer >= OBSTACLE_SPAWN_INTERVAL:
            self.spawn_obstacle()
            self.spawn_timer = 0

        for obs in self.obstacles[:]:
            obs.update(self.current_speed)
            if obs.off_screen():
                self.obstacles.remove(obs)

        self.update_score()

        if self.check_collisions():
            self.game_active = False
            self.game_over = True

        # Parallax scrolling
        self.scroll_offset = (self.scroll_offset + self.current_speed * 0.5) % SCREEN_WIDTH

        # Update clouds
        for cloud in self.clouds:
            cloud['x'] -= cloud['speed']
            if cloud['x'] < -100:
                cloud['x'] = SCREEN_WIDTH + 50
                cloud['y'] = random.randint(30, 120)

    def draw_background(self):
        # Sky gradient
        for y in range(SCREEN_HEIGHT):
            color_val = 135 + int(100 * y / SCREEN_HEIGHT)
            pygame.draw.line(self.screen, (color_val, 206, 235), (0, y), (SCREEN_WIDTH, y))

        # Mountains (parallax)
        for points in self.mountain_points:
            shifted_points = [(x - self.scroll_offset * 0.3, y) for (x, y) in points]
            pygame.draw.polygon(self.screen, MOUNTAIN_COLOR, shifted_points)
            pygame.draw.polygon(self.screen, (80, 80, 100), shifted_points, 2)

        # Clouds
        for cloud in self.clouds:
            x = cloud['x']
            y = cloud['y']
            size = cloud['size']
            # Draw semi-transparent white circles for cloud effect
            cloud_surf = pygame.Surface((size*2, size), pygame.SRCALPHA)
            pygame.draw.circle(cloud_surf, (*WHITE, 180), (size//2, size//2), size//2)
            pygame.draw.circle(cloud_surf, (*WHITE, 180), (size, size//3), size//2)
            pygame.draw.circle(cloud_surf, (*WHITE, 180), (size*3//2, size//2), size//2)
            self.screen.blit(cloud_surf, (x, y))

        # Ground
        pygame.draw.rect(self.screen, GROUND_COLOR,
                         (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
        pygame.draw.rect(self.screen, GROUND_TOP_COLOR,
                         (0, GROUND_Y, SCREEN_WIDTH, 5))

        # Ground pattern (scrolling)
        for i in range(-1, SCREEN_WIDTH//30 + 2):
            x = (i * 30 - self.scroll_offset) % (SCREEN_WIDTH + 60) - 30
            pygame.draw.rect(self.screen, (20, 100, 20), (x, GROUND_Y+10, 15, 5))
            pygame.draw.rect(self.screen, (20, 100, 20), (x+15, GROUND_Y+20, 10, 5))

    def draw_ui(self):
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))

        speed_text = self.font.render(f"Speed: {self.current_speed:.1f}", True, BLACK)
        self.screen.blit(speed_text, (SCREEN_WIDTH - 150, 10))

        if not self.game_active and not self.game_over:
            # Title with shadow
            title = self.big_font.render("DRAGON RUNNER", True, DARK_GREEN)
            title_shadow = self.big_font.render("DRAGON RUNNER", True, BLACK)
            self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 3, SCREEN_HEIGHT//2 - 80 + 3))
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 80))

            prompt1 = self.font.render("Press SPACE to Start", True, BLACK)
            prompt2 = self.font.render("SPACE or UP to Jump", True, BLACK)
            self.screen.blit(prompt1, (SCREEN_WIDTH//2 - prompt1.get_width()//2, SCREEN_HEIGHT//2))
            self.screen.blit(prompt2, (SCREEN_WIDTH//2 - prompt2.get_width()//2, SCREEN_HEIGHT//2 + 40))

        if self.game_over:
            over_text = self.big_font.render("GAME OVER", True, RED)
            over_shadow = self.big_font.render("GAME OVER", True, BLACK)
            self.screen.blit(over_shadow, (SCREEN_WIDTH//2 - over_text.get_width()//2 + 3, SCREEN_HEIGHT//2 - 60 + 3))
            self.screen.blit(over_text, (SCREEN_WIDTH//2 - over_text.get_width()//2, SCREEN_HEIGHT//2 - 60))

            final_score = self.font.render(f"Score: {self.score}", True, BLACK)
            restart_text = self.font.render("Press R to Restart", True, BLACK)
            self.screen.blit(final_score, (SCREEN_WIDTH//2 - final_score.get_width()//2, SCREEN_HEIGHT//2))
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 40))

    def draw(self):
        self.draw_background()
        for obs in self.obstacles:
            obs.draw(self.screen)
        self.dragon.draw(self.screen)
        self.draw_ui()
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()