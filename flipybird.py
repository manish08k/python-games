import pygame
import random
import sys

# ---------- CONSTANTS ----------
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.25         # reduced for slower fall
JUMP_STRENGTH = -6      # softer jump
PIPE_WIDTH = 70
PIPE_GAP = 180
PIPE_SPEED = 3
PIPE_SPAWN_INTERVAL = 90   # shorter interval → pipes appear faster
GROUND_HEIGHT = 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
BLUE = (135, 206, 235)
RED = (255, 0, 0)


# ---------- BIRD CLASS ----------
class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.radius = 12
        self.rect = pygame.Rect(x - self.radius, y - self.radius,
                                self.radius * 2, self.radius * 2)

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x + 4), int(self.y - 4)), 3)

    def get_rect(self):
        return self.rect


# ---------- PIPE CLASS ----------
class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = PIPE_WIDTH
        self.gap_y = random.randint(150, SCREEN_HEIGHT - GROUND_HEIGHT - 150)
        self.top_height = self.gap_y - PIPE_GAP // 2
        self.bottom_y = self.gap_y + PIPE_GAP // 2
        self.passed = False

        self.top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        self.bottom_rect = pygame.Rect(self.x, self.bottom_y, self.width,
                                       SCREEN_HEIGHT - GROUND_HEIGHT - self.bottom_y)

    def update(self, speed):
        self.x -= speed
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.top_rect)
        pygame.draw.rect(screen, GREEN, self.bottom_rect)
        pygame.draw.rect(screen, (0, 150, 0), (self.x - 5, self.top_height - 20,
                                               self.width + 10, 20))
        pygame.draw.rect(screen, (0, 150, 0), (self.x - 5, self.bottom_y,
                                               self.width + 10, 20))

    def off_screen(self):
        return self.x + self.width < 0

    def collide(self, bird_rect):
        return self.top_rect.colliderect(bird_rect) or self.bottom_rect.colliderect(bird_rect)


# ---------- GAME CLASS ----------
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 36, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 24)

        self._init_sounds()

        self.reset_game()
        self.state = "START"
        self.score = 0
        self.high_score = 0

        self.pipe_speed = PIPE_SPEED
        self.spawn_timer = 0

    def _init_sounds(self):
        """Try to load sound files; disable sound if missing."""
        self.sounds_enabled = True
        try:
            self.jump_sound = pygame.mixer.Sound("jump.wav")
            self.hit_sound = pygame.mixer.Sound("hit.wav")
            self.score_sound = pygame.mixer.Sound("score.wav")
        except FileNotFoundError:
            self.sounds_enabled = False
            self.jump_sound = None
            self.hit_sound = None
            self.score_sound = None

    def reset_game(self):
        self.bird = Bird(100, SCREEN_HEIGHT // 2)
        self.pipes = []
        self.score = 0
        self.pipe_speed = PIPE_SPEED
        # Start with timer almost full so first pipe appears quickly
        self.spawn_timer = PIPE_SPAWN_INTERVAL - 20

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == "START":
                        self.state = "PLAYING"
                        self.reset_game()
                    elif self.state == "PLAYING":
                        self.bird.jump()
                        if self.sounds_enabled:
                            self.jump_sound.play()
                    elif self.state == "GAME_OVER":
                        self.state = "START"

    def update(self):
        if self.state != "PLAYING":
            return

        self.bird.update()

        # Pipe spawning
        self.spawn_timer += 1
        if self.spawn_timer >= PIPE_SPAWN_INTERVAL:
            self.pipes.append(Pipe(SCREEN_WIDTH))
            self.spawn_timer = 0
            self.pipe_speed = min(6, PIPE_SPEED + self.score // 10)

        # Update pipes and scoring
        for pipe in self.pipes[:]:
            pipe.update(self.pipe_speed)
            if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                pipe.passed = True
                self.score += 1
                if self.sounds_enabled:
                    self.score_sound.play()
            if pipe.off_screen():
                self.pipes.remove(pipe)

        # Collisions
        bird_rect = self.bird.get_rect()
        if bird_rect.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT or bird_rect.top <= 0:
            self.game_over()
        for pipe in self.pipes:
            if pipe.collide(bird_rect):
                self.game_over()
                break

    def game_over(self):
        self.state = "GAME_OVER"
        if self.sounds_enabled:
            self.hit_sound.play()
        if self.score > self.high_score:
            self.high_score = self.score

    def draw(self):
        self.screen.fill(BLUE)

        if self.state == "START":
            self.draw_start_screen()
        elif self.state == "PLAYING":
            for pipe in self.pipes:
                pipe.draw(self.screen)
            pygame.draw.rect(self.screen, (34, 139, 34),
                             (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
            self.bird.draw(self.screen)
            score_text = self.font.render(str(self.score), True, WHITE)
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 30))
        elif self.state == "GAME_OVER":
            for pipe in self.pipes:
                pipe.draw(self.screen)
            pygame.draw.rect(self.screen, (34, 139, 34),
                             (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
            self.bird.draw(self.screen)
            score_text = self.font.render(str(self.score), True, WHITE)
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 30))
            self.draw_game_over_screen()

        pygame.display.update()

    def draw_start_screen(self):
        title = self.font.render("FLAPPY BIRD", True, YELLOW)
        start = self.small_font.render("Press SPACE to Start", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 60))
        self.screen.blit(start, (SCREEN_WIDTH//2 - start.get_width()//2, SCREEN_HEIGHT//2))
        if self.high_score > 0:
            hs_text = self.small_font.render(f"High Score: {self.high_score}", True, WHITE)
            self.screen.blit(hs_text, (SCREEN_WIDTH//2 - hs_text.get_width()//2, SCREEN_HEIGHT//2 + 40))

    def draw_game_over_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        go_text = self.font.render("GAME OVER", True, RED)
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        restart = self.small_font.render("Press SPACE to Play Again", True, WHITE)
        self.screen.blit(go_text, (SCREEN_WIDTH//2 - go_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 20))
        self.screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, SCREEN_HEIGHT//2 + 20))
        if self.high_score > 0:
            hs_text = self.small_font.render(f"High Score: {self.high_score}", True, WHITE)
            self.screen.blit(hs_text, (SCREEN_WIDTH//2 - hs_text.get_width()//2, SCREEN_HEIGHT//2 + 60))

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()