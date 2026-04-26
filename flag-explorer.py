import pygame
import random
import json
import os
import sys
import math

# Initialize
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flag Explorer - Learn World Flags")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (50, 255, 50)
RED = (255, 50, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 50)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230)

# Fonts
font_large = pygame.font.Font(None, 52)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 28)

# ---------- Flag Database (Simplified with color stripes) ----------
# For a real game, you would use actual flag images.
# Here we use colored stripes to represent flags.
COUNTRIES = [
    {"name": "France", "colors": [(0, 85, 164), (255, 255, 255), (239, 65, 53)], "pattern": "vertical"},
    {"name": "Germany", "colors": [(0, 0, 0), (255, 0, 0), (255, 204, 0)], "pattern": "horizontal"},
    {"name": "Italy", "colors": [(0, 140, 69), (255, 255, 255), (205, 33, 42)], "pattern": "vertical"},
    {"name": "Japan", "colors": [(255, 255, 255), (188, 0, 45)], "pattern": "circle"},
    {"name": "Brazil", "colors": [(0, 156, 59), (255, 223, 0), (0, 39, 118)], "pattern": "diamond"},
    {"name": "India", "colors": [(255, 103, 31), (255, 255, 255), (18, 136, 7)], "pattern": "horizontal"},
    {"name": "Canada", "colors": [(255, 255, 255), (255, 0, 0)], "pattern": "vertical_pale"},
    {"name": "Russia", "colors": [(255, 255, 255), (0, 57, 166), (213, 43, 30)], "pattern": "horizontal"},
    {"name": "United Kingdom", "colors": [(0, 36, 125), (255, 255, 255), (200, 16, 46)], "pattern": "union"},
    {"name": "Spain", "colors": [(198, 11, 31), (255, 193, 37), (198, 11, 31)], "pattern": "horizontal_stripe"},
    {"name": "Mexico", "colors": [(0, 104, 71), (255, 255, 255), (206, 17, 38)], "pattern": "vertical"},
    {"name": "South Africa", "colors": [(0, 56, 128), (255, 184, 28), (0, 119, 73), (255, 255, 255), (224, 60, 49)], "pattern": "horizontal_y"},
    {"name": "Argentina", "colors": [(117, 170, 219), (255, 255, 255), (117, 170, 219)], "pattern": "horizontal_sun"},
    {"name": "Australia", "colors": [(1, 33, 105), (255, 255, 255), (202, 45, 45)], "pattern": "union_stars"},
    {"name": "China", "colors": [(238, 28, 37), (255, 255, 0)], "pattern": "stars"},
    {"name": "Egypt", "colors": [(206, 17, 38), (255, 255, 255), (0, 0, 0)], "pattern": "horizontal_eagle"},
    {"name": "Nigeria", "colors": [(0, 128, 0), (255, 255, 255), (0, 128, 0)], "pattern": "vertical"},
    {"name": "Pakistan", "colors": [(0, 64, 26), (255, 255, 255)], "pattern": "crescent"},
]

# For randomized wrong answers
ALL_NAMES = [c["name"] for c in COUNTRIES]

class Flag:
    def __init__(self, country):
        self.country = country
        self.name = country["name"]
        self.colors = country["colors"]
        self.pattern = country["pattern"]
        self.flag_surface = self.create_flag()
        self.rect = self.flag_surface.get_rect()

    def create_flag(self):
        """Create a flag surface based on country's pattern."""
        width, height = 300, 200
        flag = pygame.Surface((width, height))
        flag.fill(WHITE)

        if self.pattern == "vertical":
            stripe_w = width // len(self.colors)
            for i, color in enumerate(self.colors):
                pygame.draw.rect(flag, color, (i * stripe_w, 0, stripe_w, height))
        elif self.pattern == "horizontal":
            stripe_h = height // len(self.colors)
            for i, color in enumerate(self.colors):
                pygame.draw.rect(flag, color, (0, i * stripe_h, width, stripe_h))
        elif self.pattern == "circle":
            flag.fill(self.colors[0])
            center = (width // 2, height // 2)
            radius = min(width, height) // 3
            pygame.draw.circle(flag, self.colors[1], center, radius)
        elif self.pattern == "vertical_pale":
            mid = width // 3
            flag.fill(self.colors[1])
            pygame.draw.rect(flag, self.colors[0], (0, 0, mid, height))
            pygame.draw.rect(flag, self.colors[0], (2 * mid, 0, mid, height))
        elif self.pattern == "diamond":
            flag.fill(self.colors[0])
            diamond = [(width // 2, 0), (width, height // 2), (width // 2, height), (0, height // 2)]
            pygame.draw.polygon(flag, self.colors[1], diamond)
            # Add a small circle for Brazil
            if self.name == "Brazil":
                pygame.draw.circle(flag, self.colors[2], (width // 2, height // 2), 30)
        elif self.pattern == "horizontal_y":
            flag.fill(self.colors[0])
            # Simplified Y shape
            points = [(0, 0), (0, height // 2), (width // 2, height // 2), (width, 0)]
            pygame.draw.polygon(flag, self.colors[1], points)
        else:
            # Default to vertical stripes
            stripe_w = width // len(self.colors)
            for i, color in enumerate(self.colors):
                pygame.draw.rect(flag, color, (i * stripe_w, 0, stripe_w, height))

        return flag

    def draw(self, screen, x, y):
        screen.blit(self.flag_surface, (x, y))

class Button:
    def __init__(self, text, x, y, width, height, color, hover_color):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        text_surf = font_medium.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click[0]

class FlagExplorer:
    def __init__(self):
        self.questions = COUNTRIES.copy()
        self.current_question = None
        self.options = []
        self.score = 0
        self.current_round = 0
        self.total_rounds = len(self.questions)
        self.game_over = False
        self.feedback = ""
        self.feedback_timer = 0
        self.selected_option = -1
        self.correct_answer = False
        self.waiting_for_next = False
        self.next_timer = 0
        self.highscore = self.load_highscore()
        self.init_ui()

    def load_highscore(self):
        try:
            with open("flag_explorer_highscore.json", "r") as f:
                data = json.load(f)
                return data.get("highscore", 0)
        except:
            return 0

    def save_highscore(self):
        if self.score > self.highscore:
            self.highscore = self.score
            with open("flag_explorer_highscore.json", "w") as f:
                json.dump({"highscore": self.highscore}, f)

    def init_ui(self):
        # Create answer buttons (4 options)
        button_width = 200
        button_height = 50
        start_y = HEIGHT - 150
        spacing = (WIDTH - 4 * button_width) // 5
        self.answer_buttons = []
        for i in range(4):
            x = spacing + i * (button_width + spacing)
            self.answer_buttons.append(
                Button("", x, start_y, button_width, button_height, BLUE, LIGHT_BLUE)
            )
        # Restart button
        self.restart_button = Button(
            "Restart", WIDTH - 100, 20, 80, 40, RED, ORANGE
        )

    def load_new_question(self):
        if self.current_round >= self.total_rounds:
            self.game_over = True
            self.save_highscore()
            return

        self.current_question = self.questions[self.current_round]
        # Generate random wrong options
        wrong_names = [c["name"] for c in self.questions if c["name"] != self.current_question["name"]]
        other_options = random.sample(wrong_names, 3)
        self.options = other_options + [self.current_question["name"]]
        random.shuffle(self.options)

        # Update button texts
        for i, btn in enumerate(self.answer_buttons):
            btn.text = self.options[i]

        self.feedback = ""
        self.feedback_timer = 0
        self.selected_option = -1
        self.correct_answer = False
        self.waiting_for_next = False

    def check_answer(self, selected_idx):
        selected = self.options[selected_idx]
        correct = (selected == self.current_question["name"])
        self.selected_option = selected_idx
        self.correct_answer = correct

        if correct:
            points = 10
            self.score += points
            self.feedback = f"Correct! +{points} points"
            self.feedback_color = GREEN
        else:
            self.feedback = f"Wrong! The correct answer is {self.current_question['name']}"
            self.feedback_color = RED

        self.feedback_timer = 90  # 1.5 seconds at 60 fps
        self.waiting_for_next = True
        self.next_timer = 90

    def update(self):
        if self.game_over:
            return
        if self.waiting_for_next:
            if self.next_timer > 0:
                self.next_timer -= 1
            else:
                self.waiting_for_next = False
                self.current_round += 1
                if self.current_round < self.total_rounds:
                    self.load_new_question()
                else:
                    self.game_over = True
                    self.save_highscore()
            return
        if self.feedback_timer > 0:
            self.feedback_timer -= 1

    def handle_events(self, events, mouse_pos, mouse_click):
        if self.game_over:
            # Restart button on game over screen
            if self.restart_button.is_clicked(mouse_pos, mouse_click):
                self.__init__()
                self.start_game()
            return

        # Restart button
        if self.restart_button.is_clicked(mouse_pos, mouse_click):
            self.__init__()
            self.start_game()
            return

        if not self.waiting_for_next:
            for i, btn in enumerate(self.answer_buttons):
                btn.update(mouse_pos)
                if btn.is_clicked(mouse_pos, mouse_click):
                    self.check_answer(i)

    def start_game(self):
        self.questions = random.sample(self.questions, len(self.questions))
        self.current_round = 0
        self.score = 0
        self.game_over = False
        self.load_new_question()

    def draw(self, screen):
        screen.fill(BLACK)

        if self.game_over:
            self.draw_game_over(screen)
            # Draw restart button
            self.restart_button.draw(screen)
            return

        # Draw flag
        if self.current_question:
            flag = Flag(self.current_question)
            flag_x = (WIDTH - flag.rect.width) // 2
            flag_y = 100
            flag.draw(screen, flag_x, flag_y)

            # Draw country name hint (optional)
            hint = font_medium.render("Which country does this flag belong to?", True, WHITE)
            screen.blit(hint, (WIDTH//2 - hint.get_width()//2, flag_y + flag.rect.height + 20))

        # Draw answer buttons
        for btn in self.answer_buttons:
            btn.draw(screen)

        # Draw score and progress
        score_text = font_medium.render(f"Score: {self.score}", True, GREEN)
        progress_text = font_medium.render(f"Question: {self.current_round + 1}/{self.total_rounds}", True, WHITE)
        high_text = font_small.render(f"High Score: {self.highscore}", True, YELLOW)
        screen.blit(score_text, (20, 20))
        screen.blit(progress_text, (20, 60))
        screen.blit(high_text, (20, 100))

        # Draw restart button
        self.restart_button.draw(screen)

        # Draw feedback
        if self.feedback_timer > 0:
            feedback_surf = font_medium.render(self.feedback, True, self.feedback_color)
            feedback_rect = feedback_surf.get_rect(center=(WIDTH//2, HEIGHT - 80))
            screen.blit(feedback_surf, feedback_rect)

        # Highlight selected answer
        if self.selected_option != -1:
            btn = self.answer_buttons[self.selected_option]
            color = GREEN if self.correct_answer else RED
            pygame.draw.rect(screen, color, btn.rect.inflate(10, 10), 4)

    def draw_game_over(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        game_over_text = font_large.render("FLAG EXPLORER - GAME OVER", True, WHITE)
        final_score = font_medium.render(f"Final Score: {self.score}", True, YELLOW)
        high_score = font_medium.render(f"High Score: {self.highscore}", True, GREEN)
        restart_text = font_small.render("Click 'Restart' to play again", True, WHITE)

        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, 200))
        screen.blit(final_score, (WIDTH//2 - final_score.get_width()//2, 280))
        screen.blit(high_score, (WIDTH//2 - high_score.get_width()//2, 330))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 400))

def main():
    game = FlagExplorer()
    game.start_game()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        game.handle_events(events, mouse_pos, mouse_click)
        game.update()
        game.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()