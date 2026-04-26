import pygame
import random
import math

# Initialize
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids Defender - Shoot Up!")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# ------------------------------------------------------------
# Bullet (goes upward)
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 4
        self.speed = 8
        self.life = 90  # frames

    def update(self):
        self.y -= self.speed
        self.life -= 1
        return self.life > 0 and self.y > 0

    def draw(self, surf):
        pygame.draw.circle(surf, YELLOW, (int(self.x), int(self.y)), self.radius)

# ------------------------------------------------------------
# Asteroid (falls from top)
class Asteroid:
    def __init__(self):
        self.x = random.randint(30, WIDTH - 30)
        self.y = -random.randint(20, 100)
        self.size = random.choice(['small', 'medium', 'large'])
        if self.size == 'large':
            self.radius = 25
            self.score = 20
            self.speed = random.uniform(1, 2)
        elif self.size == 'medium':
            self.radius = 15
            self.score = 50
            self.speed = random.uniform(2, 3)
        else:
            self.radius = 8
            self.score = 100
            self.speed = random.uniform(3, 5)
        # slight horizontal drift
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = self.speed

    def update(self):
        self.x += self.vx
        self.y += self.vy
        return self.y < HEIGHT + 50  # remove if below screen

    def draw(self, surf):
        # rough polygon for asteroid look
        points = []
        for i in range(8):
            rad = i * math.pi * 2 / 8
            r = self.radius + random.randint(-3, 3)
            px = self.x + r * math.cos(rad)
            py = self.y + r * math.sin(rad)
            points.append((px, py))
        color = (150, 150, 150)
        pygame.draw.polygon(surf, color, points, 2)

    def split(self, asteroids):
        # if large, spawn two medium; if medium, two small
        if self.size == 'large':
            for _ in range(2):
                new_ast = Asteroid()
                new_ast.size = 'medium'
                new_ast.radius = 15
                new_ast.score = 50
                new_ast.speed = random.uniform(2, 3)
                new_ast.x = self.x + random.randint(-15, 15)
                new_ast.y = self.y
                asteroids.append(new_ast)
        elif self.size == 'medium':
            for _ in range(2):
                new_ast = Asteroid()
                new_ast.size = 'small'
                new_ast.radius = 8
                new_ast.score = 100
                new_ast.speed = random.uniform(3, 5)
                new_ast.x = self.x + random.randint(-10, 10)
                new_ast.y = self.y
                asteroids.append(new_ast)
        # small asteroids just disappear

# ------------------------------------------------------------
# Power-up (falls from top)
class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.type = random.choice(['extra_life', 'rapid_fire', 'shield'])
        self.speed = 2

    def update(self):
        self.y += self.speed
        return self.y < HEIGHT + 30

    def draw(self, surf):
        color = {'extra_life': RED, 'rapid_fire': GREEN, 'shield': BLUE}[self.type]
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.radius)
        # draw symbol
        if self.type == 'extra_life':
            pygame.draw.line(surf, WHITE, (self.x-5, self.y), (self.x+5, self.y), 2)
            pygame.draw.line(surf, WHITE, (self.x, self.y-5), (self.x, self.y+5), 2)
        elif self.type == 'rapid_fire':
            pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), 3)
        elif self.type == 'shield':
            pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), 6, 2)

# ------------------------------------------------------------
# Ship (moves left/right at bottom)
class Ship:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 60
        self.width = 30
        self.height = 30
        self.speed = 6
        self.alive = True
        self.invincible_timer = 0
        self.shoot_cooldown = 0
        self.shoot_delay = 15   # frames between shots (normal)
        self.rapid_fire = False
        self.rapid_fire_timer = 0

    def update(self, keys):
        if not self.alive:
            return

        # left/right movement
        if keys[pygame.K_LEFT] and self.x > 20:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - 20:
            self.x += self.speed

        # shoot with space
        if keys[pygame.K_SPACE] and self.shoot_cooldown <= 0:
            self.shoot_cooldown = 5 if self.rapid_fire else self.shoot_delay
            return True   # indicates shoot
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # rapid fire power-up timer
        if self.rapid_fire:
            self.rapid_fire_timer -= 1
            if self.rapid_fire_timer <= 0:
                self.rapid_fire = False

        # invincibility frames after hit
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        return False

    def draw(self, surf):
        if not self.alive:
            return
        # blink if invincible
        if self.invincible_timer > 0 and (self.invincible_timer // 5) % 2 == 0:
            return
        # draw ship as triangle pointing up
        points = [(self.x, self.y - 15),
                  (self.x - 15, self.y + 10),
                  (self.x + 15, self.y + 10)]
        pygame.draw.polygon(surf, WHITE, points, 2)
        # draw shield effect if rapid fire active (visual)
        if self.rapid_fire:
            pygame.draw.circle(surf, GREEN, (int(self.x), int(self.y-5)), 20, 2)

    def hit(self):
        if self.invincible_timer <= 0 and self.alive:
            self.alive = False
            return True
        return False

    def respawn(self):
        self.x = WIDTH // 2
        self.alive = True
        self.invincible_timer = 60   # 1 second invincibility
        self.shoot_cooldown = 0

# ------------------------------------------------------------
# Main game
def game():
    ship = Ship()
    bullets = []
    asteroids = []
    powerups = []
    score = 0
    lives = 3
    respawn_timer = 0
    game_over = False
    wave_timer = 0
    wave_delay = 90   # frames between wave spawns

    # initial wave of asteroids
    for _ in range(6):
        asteroids.append(Asteroid())

    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    return game()
                if event.key == pygame.K_q and game_over:
                    return

        if game_over:
            screen.fill(BLACK)
            text = big_font.render("GAME OVER", True, WHITE)
            score_text = font.render(f"Score: {score}", True, WHITE)
            restart_text = font.render("Press R to restart, Q to quit", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 280))
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 360))
            pygame.display.flip()
            continue

        keys = pygame.key.get_pressed()
        shoot = ship.update(keys)

        if shoot:
            bullets.append(Bullet(ship.x, ship.y - 15))

        # respawn logic
        if not ship.alive:
            if respawn_timer <= 0:
                if lives > 0:
                    ship.respawn()
                    lives -= 1
                else:
                    game_over = True
            else:
                respawn_timer -= 1
        else:
            # spawn new waves periodically
            wave_timer += 1
            if wave_timer >= wave_delay and len(asteroids) < 15:
                wave_timer = 0
                for _ in range(random.randint(2, 4)):
                    asteroids.append(Asteroid())

        # update bullets
        for b in bullets[:]:
            if not b.update():
                bullets.remove(b)

        # update asteroids
        for a in asteroids[:]:
            if not a.update():
                asteroids.remove(a)

        # update powerups
        for pu in powerups[:]:
            if not pu.update():
                powerups.remove(pu)

        # collisions: bullets vs asteroids
        for b in bullets[:]:
            for a in asteroids[:]:
                if math.hypot(b.x - a.x, b.y - a.y) < b.radius + a.radius:
                    # bullet hits asteroid
                    bullets.remove(b)
                    score += a.score
                    a.split(asteroids)
                    asteroids.remove(a)
                    # 15% chance drop power-up
                    if random.random() < 0.15:
                        powerups.append(PowerUp(a.x, a.y))
                    break   # bullet destroyed

        # collisions: ship vs asteroids
        if ship.alive and ship.invincible_timer <= 0:
            for a in asteroids:
                if math.hypot(ship.x - a.x, ship.y - a.y) < 15 + a.radius:
                    if ship.hit():
                        ship.alive = False
                        respawn_timer = 45   # 0.75 sec delay
                        # optional: destroy the asteroid that hit you
                        asteroids.remove(a)
                        score += a.score   # slight compensation
                    break

        # collisions: ship vs powerups
        if ship.alive:
            for pu in powerups[:]:
                if math.hypot(ship.x - pu.x, ship.y - pu.y) < 15 + pu.radius:
                    if pu.type == 'extra_life':
                        lives += 1
                    elif pu.type == 'rapid_fire':
                        ship.rapid_fire = True
                        ship.rapid_fire_timer = 300   # 5 seconds
                    elif pu.type == 'shield':
                        ship.invincible_timer = 90   # temporary shield
                    powerups.remove(pu)

        # Drawing
        screen.fill(BLACK)

        # UI
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        status = "RAPID FIRE" if ship.rapid_fire else "Normal"
        status_color = GREEN if ship.rapid_fire else WHITE
        status_text = font.render(status, True, status_color)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        screen.blit(status_text, (10, 90))

        for a in asteroids:
            a.draw(screen)
        for b in bullets:
            b.draw(screen)
        for pu in powerups:
            pu.draw(screen)
        ship.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    game()