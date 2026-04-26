import pygame
import random
import sys
import json
import os
import math

# Initialize
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Word Rescue - Advanced")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 50)
PURPLE = (200, 50, 200)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)

# Fonts
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# Word list (normal)
NORMAL_WORDS = [
    "PYTHON", "GAME", "CODE", "FALL", "TYPE", "SAVE", "HELP", "WORD",
    "FAST", "QUICK", "RESCUE", "CLICK", "KEY", "SPEED", "LEVEL", "PLAY",
    "FUN", "LEARN", "CODE", "BUG", "FIX"
]

# Golden words (rare, give bonus)
GOLDEN_WORDS = ["JACKPOT", "BONUS", "GOLDEN", "WINNER", "LUCKY"]

# Power-up types
POWERUPS = ["extra_life", "slow_time", "double_points", "clear_screen", "magnet"]

# Settings
BASE_FALL_SPEED = 2.0          # constant, does not increase
SPAWN_DELAY = 45               # frames between new words
INITIAL_LIVES = 3
COMBO_TIMEOUT = 180            # frames (3 seconds) to keep combo alive

class Particle:
    """Simple particle effect for word explosion."""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -2)
        self.life = 30
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.life -= 1
        return self.life > 0

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), 3)

class FallingWord:
    def __init__(self, text, x, y, speed, is_golden=False):
        self.text = text
        self.x = x
        self.y = y
        self.speed = speed
        self.is_golden = is_golden
        self.font = font_medium
        self.color = YELLOW if is_golden else WHITE
        self.surface = self.font.render(text, True, self.color)
        self.rect = self.surface.get_rect(center=(x, y))
        self.active = True
        self.flash_timer = 0
        self.flash_color = None

    def update(self):
        self.y += self.speed
        self.rect.center = (self.x, self.y)
        if self.flash_timer > 0:
            self.flash_timer -= 1
            if self.flash_timer == 0:
                self.surface = self.font.render(self.text, True, self.color)
        return self.y < HEIGHT + 50

    def draw(self, surf):
        surf.blit(self.surface, self.rect)

    def flash(self, color, duration=10):
        self.flash_timer = duration
        self.surface = self.font.render(self.text, True, color)

    def check_typed(self, typed_word):
        return self.text == typed_word

class PowerUp:
    def __init__(self, x, y, ptype):
        self.x = x
        self.y = y
        self.type = ptype
        self.speed = BASE_FALL_SPEED
        self.radius = 15
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius*2, self.radius*2)

    def update(self):
        self.y += self.speed
        self.rect.center = (self.x, self.y)
        return self.y < HEIGHT + 50

    def draw(self, surf):
        color = {
            "extra_life": RED,
            "slow_time": BLUE,
            "double_points": GREEN,
            "clear_screen": PURPLE,
            "magnet": ORANGE
        }[self.type]
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), self.radius, 2)
        # symbol
        if self.type == "extra_life":
            pygame.draw.line(surf, WHITE, (self.x-6, self.y), (self.x+6, self.y), 2)
            pygame.draw.line(surf, WHITE, (self.x, self.y-6), (self.x, self.y+6), 2)
        elif self.type == "slow_time":
            pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), 6, 2)
        elif self.type == "double_points":
            pygame.draw.line(surf, WHITE, (self.x-8, self.y-5), (self.x+8, self.y+5), 2)
            pygame.draw.line(surf, WHITE, (self.x-8, self.y+5), (self.x+8, self.y-5), 2)
        elif self.type == "clear_screen":
            pygame.draw.rect(surf, WHITE, (self.x-8, self.y-8, 16, 16), 2)
        else:  # magnet
            pygame.draw.arc(surf, WHITE, (self.x-8, self.y-8, 16, 16), 0, math.pi, 2)

class WordRescueGame:
    def __init__(self):
        self.words = []
        self.powerups = []
        self.particles = []
        self.score = 0
        self.lives = INITIAL_LIVES
        self.game_over = False
        self.current_input = ""
        self.fall_speed = BASE_FALL_SPEED
        self.spawn_timer = 0
        self.message = ""
        self.message_timer = 0
        self.combo = 0
        self.combo_timer = 0
        self.multiplier = 1
        # power-up effects
        self.slow_timer = 0
        self.double_timer = 0
        self.magnet_active = False
        self.magnet_word = None
        # high score
        self.highscore = self.load_highscore()
        # golden word chance
        self.golden_chance = 0.1   # 10%

    def load_highscore(self):
        try:
            with open("word_rescue_adv_highscore.json", "r") as f:
                data = json.load(f)
                return data.get("highscore", 0)
        except:
            return 0

    def save_highscore(self):
        with open("word_rescue_adv_highscore.json", "w") as f:
            json.dump({"highscore": self.highscore}, f)

    def spawn_word(self):
        # decide golden or normal
        is_golden = random.random() < self.golden_chance
        word_list = GOLDEN_WORDS if is_golden else NORMAL_WORDS
        word = random.choice(word_list)
        x = random.randint(80, WIDTH - 80)
        y = -30
        self.words.append(FallingWord(word, x, y, self.fall_speed, is_golden))

    def spawn_powerup(self, x, y):
        ptype = random.choice(POWERUPS)
        self.powerups.append(PowerUp(x, y, ptype))

    def add_particles(self, x, y, color):
        for _ in range(15):
            self.particles.append(Particle(x, y, color))

    def update(self):
        if self.game_over:
            return

        # timers
        if self.slow_timer > 0:
            self.slow_timer -= 1
            current_speed = BASE_FALL_SPEED * 0.4
        else:
            current_speed = BASE_FALL_SPEED
        self.fall_speed = current_speed

        if self.double_timer > 0:
            self.double_timer -= 1

        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0
            self.multiplier = 1

        # spawn words
        if self.spawn_timer <= 0:
            self.spawn_word()
            self.spawn_timer = SPAWN_DELAY
        else:
            self.spawn_timer -= 1

        # update words
        for w in self.words[:]:
            if not w.update():
                self.words.remove(w)
                self.lives -= 1
                self.combo = 0
                self.multiplier = 1
                self.message = f"Missed! -1 life"
                self.message_timer = 60
                self.add_particles(w.x, w.y, RED)
                if self.lives <= 0:
                    self.game_over = True
                    if self.score > self.highscore:
                        self.highscore = self.score
                        self.save_highscore()
            else:
                # update speed for slow effect
                w.speed = self.fall_speed

        # update powerups
        for p in self.powerups[:]:
            if not p.update():
                self.powerups.remove(p)

        # update particles
        for p in self.particles[:]:
            if not p.update():
                self.particles.remove(p)

        # message timer
        if self.message_timer > 0:
            self.message_timer -= 1
        else:
            self.message = ""

        # magnet: if active, pre-fill input with the word
        if self.magnet_active and self.magnet_word is None and self.words:
            # pick nearest word? just pick first
            self.magnet_word = self.words[0].text
            self.current_input = self.magnet_word
            self.message = "Magnet active! Press Enter"
            self.message_timer = 60
            self.magnet_active = False

    def process_input(self, event):
        if self.game_over:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                typed = self.current_input.upper().strip()
                matched = None
                for w in self.words:
                    if w.check_typed(typed):
                        matched = w
                        break
                if matched:
                    self.words.remove(matched)
                    # base points
                    base_points = len(matched.text) * 10
                    if matched.is_golden:
                        base_points *= 2
                        self.message = f"GOLDEN! +{base_points} points"
                    else:
                        self.message = f"+{base_points} points"
                    # apply multiplier
                    points = int(base_points * self.multiplier)
                    if self.double_timer > 0:
                        points *= 2
                        self.message += " (DOUBLE)"
                    self.score += points
                    self.message_timer = 45
                    # combo increase
                    self.combo += 1
                    self.combo_timer = COMBO_TIMEOUT
                    self.multiplier = min(4, 1 + self.combo // 5)
                    # flash effect
                    matched.flash(GREEN, 8)
                    self.add_particles(matched.x, matched.y, GREEN)
                    # chance to spawn power-up from correct word
                    if random.random() < 0.15:
                        self.spawn_powerup(matched.x, matched.y)
                else:
                    self.message = "Wrong word!"
                    self.message_timer = 30
                    # flash all words red (optional)
                    for w in self.words:
                        w.flash(RED, 5)
                    # reset combo
                    self.combo = 0
                    self.multiplier = 1
                self.current_input = ""
                self.magnet_word = None
            elif event.key == pygame.K_BACKSPACE:
                self.current_input = self.current_input[:-1]
                if self.magnet_word:
                    self.magnet_word = None
            else:
                if event.unicode.isalpha():
                    self.current_input += event.unicode.upper()
                    if self.magnet_word:
                        self.magnet_word = None

    def check_powerup_collision(self, basket_rect):
        for p in self.powerups[:]:
            if basket_rect.colliderect(p.rect):
                # apply power-up effect
                if p.type == "extra_life":
                    self.lives += 1
                    self.message = "Extra life!"
                elif p.type == "slow_time":
                    self.slow_timer = 300  # 5 seconds
                    self.message = "Slow time!"
                elif p.type == "double_points":
                    self.double_timer = 600  # 10 seconds
                    self.message = "Double points!"
                elif p.type == "clear_screen":
                    self.words.clear()
                    self.message = "Screen cleared!"
                    self.add_particles(WIDTH//2, HEIGHT//2, WHITE)
                elif p.type == "magnet":
                    self.magnet_active = True
                    self.message = "Magnet active!"
                self.message_timer = 60
                self.powerups.remove(p)
                self.add_particles(p.x, p.y, BLUE)

    def draw(self, surf):
        surf.fill(BLACK)

        # draw falling words
        for w in self.words:
            w.draw(surf)

        # draw powerups
        for p in self.powerups:
            p.draw(surf)

        # draw particles
        for p in self.particles:
            p.draw(surf)

        # draw input box (basket)
        input_rect = pygame.Rect(50, HEIGHT - 70, WIDTH - 100, 50)
        pygame.draw.rect(surf, WHITE, input_rect, 2)
        input_surface = font_medium.render(self.current_input, True, WHITE)
        surf.blit(input_surface, (input_rect.x + 10, input_rect.y + 10))

        # labels
        label = font_small.render("Type the word and press ENTER", True, YELLOW)
        surf.blit(label, (input_rect.x + 10, input_rect.y - 25))

        # UI: score, lives, multiplier, highscore
        score_txt = font_large.render(f"Score: {self.score}", True, GREEN)
        lives_txt = font_large.render(f"Lives: {self.lives}", True, RED)
        multi_txt = font_medium.render(f"x{self.multiplier}", True, ORANGE)
        high_txt = font_small.render(f"High Score: {self.highscore}", True, WHITE)
        surf.blit(score_txt, (20, 20))
        surf.blit(lives_txt, (20, 80))
        surf.blit(multi_txt, (20, 140))
        surf.blit(high_txt, (20, 180))

        # active power-up indicators
        if self.slow_timer > 0:
            slow_icon = font_small.render("SLOW TIME", True, BLUE)
            surf.blit(slow_icon, (WIDTH - 150, 20))
        if self.double_timer > 0:
            double_icon = font_small.render("DOUBLE POINTS", True, GREEN)
            surf.blit(double_icon, (WIDTH - 150, 50))
        if self.combo > 0:
            combo_icon = font_small.render(f"Combo: {self.combo}", True, YELLOW)
            surf.blit(combo_icon, (WIDTH - 150, 80))

        # message
        if self.message_timer > 0:
            msg_surf = font_medium.render(self.message, True, ORANGE)
            msg_rect = msg_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
            surf.blit(msg_surf, msg_rect)

        # game over overlay
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            surf.blit(overlay, (0, 0))
            go_text = font_large.render("GAME OVER", True, RED)
            final_score = font_medium.render(f"Final Score: {self.score}", True, WHITE)
            restart = font_medium.render("Press R to restart, Q to quit", True, YELLOW)
            surf.blit(go_text, (WIDTH//2 - go_text.get_width()//2, 200))
            surf.blit(final_score, (WIDTH//2 - final_score.get_width()//2, 280))
            surf.blit(restart, (WIDTH//2 - restart.get_width()//2, 360))

def main():
    game = WordRescueGame()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game.game_over:
                    game = WordRescueGame()
                elif event.key == pygame.K_q and game.game_over:
                    running = False
                else:
                    game.process_input(event)

        game.update()
        # collision detection for power-ups: use input box as basket
        basket_rect = pygame.Rect(50, HEIGHT - 70, WIDTH - 100, 50)
        game.check_powerup_collision(basket_rect)
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()