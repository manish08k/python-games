import pygame
import random

# Initialize
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Egg Catching Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 100)

# ------------------------------------------------------------
# Egg class
class Egg:
    def __init__(self):
        self.x = random.randint(30, WIDTH - 30)
        self.y = -20
        self.radius = 12
        self.speed = random.uniform(3, 6)
        self.color = YELLOW

    def update(self):
        self.y += self.speed
        return self.y < HEIGHT + 50

    def draw(self, surf):
        # draw an egg shape (oval)
        pygame.draw.ellipse(surf, self.color, (self.x - self.radius, self.y - self.radius//2,
                                               self.radius*2, self.radius))
        # highlight
        pygame.draw.ellipse(surf, (255,255,200), (self.x - self.radius//2, self.y - self.radius//3,
                                                 self.radius, self.radius//2))

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius//2, self.radius*2, self.radius)

# ------------------------------------------------------------
# Basket (catcher)
class Basket:
    def __init__(self):
        self.width = 80
        self.height = 25
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 60
        self.speed = 8
        self.color = BROWN

    def update(self, mouse_x, keys):
        # mouse control (preferred)
        self.x = mouse_x - self.width // 2
        # also arrow keys
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        # boundaries
        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - self.width:
            self.x = WIDTH - self.width

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surf, (100, 50, 20), (self.x, self.y, self.width, self.height), 3)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# ------------------------------------------------------------
# Power-up (special bonus)
class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.type = random.choice(['extra_life', 'slow_time', 'double_points'])
        self.speed = 3

    def update(self):
        self.y += self.speed
        return self.y < HEIGHT + 30

    def draw(self, surf):
        color = {'extra_life': RED, 'slow_time': BLUE, 'double_points': GREEN}[self.type]
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.radius)
        # symbol
        if self.type == 'extra_life':
            pygame.draw.line(surf, WHITE, (self.x-4, self.y), (self.x+4, self.y), 2)
            pygame.draw.line(surf, WHITE, (self.x, self.y-4), (self.x, self.y+4), 2)
        elif self.type == 'slow_time':
            pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), 4)
        else:  # double points
            pygame.draw.line(surf, WHITE, (self.x-5, self.y-3), (self.x+5, self.y+3), 2)
            pygame.draw.line(surf, WHITE, (self.x-5, self.y+3), (self.x+5, self.y-3), 2)

# ------------------------------------------------------------
# Main game
def game():
    basket = Basket()
    eggs = []
    powerups = []
    score = 0
    lives = 3
    game_over = False
    double_points = False
    double_timer = 0
    slow_timer = 0
    spawn_counter = 0
    spawn_delay = 40  # frames between egg spawns

    running = True
    while running:
        dt = clock.tick(60)
        mouse_x, _ = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
                return game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q and game_over:
                return

        if game_over:
            screen.fill(BLACK)
            text = big_font.render("GAME OVER", True, WHITE)
            score_txt = font.render(f"Final Score: {score}", True, WHITE)
            restart_txt = font.render("Press R to restart, Q to quit", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))
            screen.blit(score_txt, (WIDTH//2 - score_txt.get_width()//2, 280))
            screen.blit(restart_txt, (WIDTH//2 - restart_txt.get_width()//2, 360))
            pygame.display.flip()
            continue

        # update basket
        basket.update(mouse_x, keys)

        # spawn eggs
        spawn_counter += 1
        if spawn_counter >= spawn_delay:
            spawn_counter = 0
            eggs.append(Egg())

        # update eggs
        for e in eggs[:]:
            if not e.update():
                eggs.remove(e)

        # update powerups
        for p in powerups[:]:
            if not p.update():
                powerups.remove(p)

        # collision: basket vs eggs
        basket_rect = basket.get_rect()
        for e in eggs[:]:
            if basket_rect.colliderect(e.get_rect()):
                eggs.remove(e)
                points = 10
                if double_points:
                    points *= 2
                score += points
                # small chance to spawn power-up when catching egg
                if random.random() < 0.1:
                    powerups.append(PowerUp(e.x, e.y))

        # collision: basket vs powerups
        for p in powerups[:]:
            if basket_rect.colliderect(pygame.Rect(p.x - p.radius, p.y - p.radius, p.radius*2, p.radius*2)):
                if p.type == 'extra_life':
                    lives += 1
                elif p.type == 'slow_time':
                    slow_timer = 300   # 5 seconds
                    # reduce speed of all falling eggs
                    for egg in eggs:
                        egg.speed = max(1, egg.speed * 0.5)
                elif p.type == 'double_points':
                    double_points = True
                    double_timer = 300
                powerups.remove(p)

        # manage power-up timers
        if double_points:
            double_timer -= 1
            if double_timer <= 0:
                double_points = False
        if slow_timer > 0:
            slow_timer -= 1
            if slow_timer <= 0:
                # restore egg speeds
                for egg in eggs:
                    egg.speed = min(6, egg.speed * 2)

        # check missed eggs (past bottom)
        for e in eggs[:]:
            if e.y + e.radius > HEIGHT:
                eggs.remove(e)
                lives -= 1
                if lives <= 0:
                    game_over = True

        # drawing
        screen.fill(BLACK)

        # draw eggs
        for e in eggs:
            e.draw(screen)

        # draw powerups
        for p in powerups:
            p.draw(screen)

        # draw basket
        basket.draw(screen)

        # UI text
        score_txt = font.render(f"Score: {score}", True, WHITE)
        lives_txt = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_txt, (10, 10))
        screen.blit(lives_txt, (10, 50))

        if double_points:
            bonus = font.render("DOUBLE POINTS", True, GREEN)
            screen.blit(bonus, (WIDTH//2 - bonus.get_width()//2, 70))
        if slow_timer > 0:
            slow_txt = font.render("SLOW TIME", True, BLUE)
            screen.blit(slow_txt, (WIDTH//2 - slow_txt.get_width()//2, 110))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    game()