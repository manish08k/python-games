import pygame
import random
import json
import os
import sys
import math

# ---------- Initialization ----------
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Simon Says")
clock = pygame.time.Clock()

# ---------- Colors ----------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
YELLOW = (200, 200, 50)
BRIGHT_RED = (255, 80, 80)
BRIGHT_GREEN = (80, 255, 80)
BRIGHT_BLUE = (80, 80, 255)
BRIGHT_YELLOW = (255, 255, 80)

# ---------- Button geometry ----------
BUTTON_SIZE = 180
GAP = 30
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2

buttons = {
    'red':    pygame.Rect(CENTER_X - BUTTON_SIZE - GAP, CENTER_Y - BUTTON_SIZE - GAP, BUTTON_SIZE, BUTTON_SIZE),
    'green':  pygame.Rect(CENTER_X + GAP, CENTER_Y - BUTTON_SIZE - GAP, BUTTON_SIZE, BUTTON_SIZE),
    'blue':   pygame.Rect(CENTER_X - BUTTON_SIZE - GAP, CENTER_Y + GAP, BUTTON_SIZE, BUTTON_SIZE),
    'yellow': pygame.Rect(CENTER_X + GAP, CENTER_Y + GAP, BUTTON_SIZE, BUTTON_SIZE)
}

color_map = {'red': RED, 'green': GREEN, 'blue': BLUE, 'yellow': YELLOW}
bright_map = {'red': BRIGHT_RED, 'green': BRIGHT_GREEN, 'blue': BRIGHT_BLUE, 'yellow': BRIGHT_YELLOW}

# ---------- Fonts ----------
font_small = pygame.font.Font(None, 36)
font_medium = pygame.font.Font(None, 48)
font_large = pygame.font.Font(None, 72)

# ---------- High score persistence ----------
HIGHSCORE_FILE = "simon_highscore.json"

def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('highscore', 0)
        except:
            return 0
    return 0

def save_highscore(score):
    with open(HIGHSCORE_FILE, 'w') as f:
        json.dump({'highscore': score}, f)

# ---------- Sound generation (graceful fallback) ----------
def safe_create_beep(frequency, duration_ms, volume=0.5):
    """Try to create a sine wave beep; if numpy not available or error, return None."""
    try:
        import numpy as np
        sample_rate = 44100
        n_samples = int(sample_rate * duration_ms / 1000)
        t = np.linspace(0, duration_ms / 1000, n_samples, endpoint=False)
        # mono wave
        wave = (4096 * np.sin(2 * np.pi * frequency * t)).astype(np.int16)
        # stereo
        stereo = np.column_stack((wave, wave))
        sound = pygame.sndarray.make_sound(stereo)
        sound.set_volume(volume)
        return sound
    except (ImportError, Exception):
        # If anything fails (no numpy, pygame.mixer not initialized, etc.), return None
        return None

# Create beeps – if a beep is None, we just skip playing
beeps = {
    'red':    safe_create_beep(523, 200),   # C5
    'green':  safe_create_beep(659, 200),   # E5
    'blue':   safe_create_beep(784, 200),   # G5
    'yellow': safe_create_beep(880, 200)    # A5
}

def play_beep(color):
    snd = beeps.get(color)
    if snd is not None:
        snd.play()

# ---------- Game class ----------
class SimonGame:
    def __init__(self):
        self.sequence = []
        self.player_sequence = []
        self.score = 0
        self.highscore = load_highscore()
        self.game_over = False
        self.waiting_for_player = False
        self.showing_sequence = False
        self.flash_timer = 0.0
        self.flash_color = None
        self.message = "Simon Says..."
        self.message_timer = 60   # frames
        self.round_num = 0
        # dynamic speed settings
        self.base_delay = 0.8
        self.flash_duration = 0.3
        # sequence playback state
        self.sequence_index = 0
        self.sequence_timer = 0.0

    def start_new_game(self):
        self.sequence = []
        self.player_sequence = []
        self.score = 0
        self.game_over = False
        self.waiting_for_player = False
        self.showing_sequence = False
        self.flash_timer = 0.0
        self.flash_color = None
        self.round_num = 0
        self.message = "Get ready..."
        self.message_timer = 60
        self.add_round()

    def add_round(self):
        self.round_num += 1
        # Add a random color
        new_color = random.choice(list(buttons.keys()))
        self.sequence.append(new_color)
        # Increase speed every 3 rounds (minimum delay 0.3, min flash 0.15)
        speed_up = min(0.5, (self.round_num // 3) * 0.05)
        self.base_delay = max(0.3, 0.8 - speed_up)
        self.flash_duration = max(0.15, 0.3 - (self.round_num // 5) * 0.02)
        self.show_sequence()

    def show_sequence(self):
        self.showing_sequence = True
        self.waiting_for_player = False
        self.player_sequence.clear()
        self.message = "Watch..."
        self.message_timer = 60
        self.sequence_index = 0
        self.sequence_timer = 0.0

    def update_sequence_display(self):
        if not self.showing_sequence:
            return
        if self.sequence_index >= len(self.sequence):
            # Finished showing
            self.showing_sequence = False
            self.waiting_for_player = True
            self.message = "Your turn!"
            self.message_timer = 60
            self.flash_color = None
            return

        if self.sequence_timer <= 0:
            # Flash next color
            color = self.sequence[self.sequence_index]
            self.flash_color = color
            play_beep(color)
            self.sequence_timer = self.flash_duration
            self.sequence_index += 1
        else:
            # Decrease timer (assuming 60 FPS)
            self.sequence_timer -= 1/60.0
            if self.sequence_timer <= 0 and self.sequence_index < len(self.sequence):
                # Turn off flash before next
                self.flash_color = None
                # Add gap between flashes
                self.sequence_timer = self.base_delay
            elif self.sequence_timer <= 0 and self.sequence_index == len(self.sequence):
                self.flash_color = None
                self.showing_sequence = False
                self.waiting_for_player = True
                self.message = "Your turn!"
                self.message_timer = 60

    def handle_button_click(self, color):
        if not self.waiting_for_player or self.game_over:
            return False
        # Feedback
        play_beep(color)
        self.flash_color = color
        self.flash_timer = self.flash_duration
        # Check correctness
        self.player_sequence.append(color)
        expected_index = len(self.player_sequence) - 1
        if color != self.sequence[expected_index]:
            # Game over
            self.game_over = True
            self.message = f"Game Over! Score: {self.score}"
            if self.score > self.highscore:
                self.highscore = self.score
                save_highscore(self.highscore)
                self.message += " NEW HIGHSCORE!"
            self.message_timer = 180
            self.waiting_for_player = False
            return False
        # If completed the whole sequence
        if len(self.player_sequence) == len(self.sequence):
            self.score += 1
            self.waiting_for_player = False
            self.message = f"Correct! +1 point (Score: {self.score})"
            self.message_timer = 90
            self.add_round()
        return True

    def update(self):
        # auto-clear flash effect
        if self.flash_timer > 0:
            self.flash_timer -= 1/60.0
            if self.flash_timer <= 0:
                self.flash_color = None
        # message lifetime
        if self.message_timer > 0:
            self.message_timer -= 1
        # sequence playback
        if self.showing_sequence:
            self.update_sequence_display()

    def draw(self, surface):
        surface.fill(BLACK)
        # Draw colored buttons
        for name, rect in buttons.items():
            color = bright_map[name] if self.flash_color == name else color_map[name]
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, WHITE, rect, 4)
            # Label
            label = font_small.render(name.capitalize(), True, WHITE)
            label_rect = label.get_rect(center=rect.center)
            surface.blit(label, label_rect)
        # UI texts
        score_surf = font_small.render(f"Score: {self.score}", True, WHITE)
        high_surf = font_small.render(f"High Score: {self.highscore}", True, WHITE)
        round_surf = font_small.render(f"Round: {self.round_num}", True, WHITE)
        surface.blit(score_surf, (20, 20))
        surface.blit(high_surf, (20, 60))
        surface.blit(round_surf, (20, 100))
        # Message
        if self.message and self.message_timer > 0:
            msg_surf = font_medium.render(self.message, True, WHITE)
            msg_rect = msg_surf.get_rect(center=(WIDTH//2, HEIGHT - 80))
            surface.blit(msg_surf, msg_rect)
        # Restart hint when game over
        if self.game_over:
            restart_surf = font_small.render("Click anywhere or press R to restart", True, WHITE)
            restart_rect = restart_surf.get_rect(center=(WIDTH//2, HEIGHT - 40))
            surface.blit(restart_surf, restart_rect)

# ---------- Main game loop ----------
def main():
    game = SimonGame()
    game.start_new_game()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.game_over:
                    game.start_new_game()
                else:
                    pos = pygame.mouse.get_pos()
                    for name, rect in buttons.items():
                        if rect.collidepoint(pos):
                            game.handle_button_click(name)
                            break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game.game_over:
                    game.start_new_game()
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()