import pygame
import json
import sys

# Initialize
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Quiz Game")
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

# Fonts
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 28)

# ---------- Question Database ----------
QUESTIONS = {
    "Science": [
        {"q": "What is the chemical symbol for Gold?", "options": ["Go", "Gd", "Au", "Ag"], "answer": 2},
        {"q": "Which planet is known as the Red Planet?", "options": ["Mars", "Jupiter", "Venus", "Saturn"], "answer": 0},
        {"q": "What is the hardest natural substance?", "options": ["Iron", "Diamond", "Gold", "Platinum"], "answer": 1},
        {"q": "What gas do plants absorb from the air?", "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"], "answer": 2},
        {"q": "Who developed the theory of relativity?", "options": ["Newton", "Galileo", "Einstein", "Tesla"], "answer": 2},
        {"q": "What is the pH of pure water?", "options": ["5", "6", "7", "8"], "answer": 2},
        {"q": "Which organ pumps blood through the body?", "options": ["Brain", "Liver", "Heart", "Lungs"], "answer": 2},
        {"q": "What is the most abundant gas in Earth's atmosphere?", "options": ["Oxygen", "Nitrogen", "Argon", "CO2"], "answer": 1},
        {"q": "Which vitamin is produced by the human skin when exposed to sunlight?", "options": ["A", "B12", "C", "D"], "answer": 3},
        {"q": "What is the study of fossils called?", "options": ["Biology", "Paleontology", "Geology", "Archaeology"], "answer": 1},
    ],
    "History": [
        {"q": "Who painted the Mona Lisa?", "options": ["Van Gogh", "Picasso", "Da Vinci", "Rembrandt"], "answer": 2},
        {"q": "Which ancient civilization built Machu Picchu?", "options": ["Aztec", "Inca", "Maya", "Olmec"], "answer": 1},
        {"q": "Who was the first President of the United States?", "options": ["Adams", "Jefferson", "Washington", "Franklin"], "answer": 2},
        {"q": "The Great Wall was built primarily in which country?", "options": ["India", "Japan", "China", "Korea"], "answer": 2},
        {"q": "Which year did World War II end?", "options": ["1943", "1944", "1945", "1946"], "answer": 2},
        {"q": "Who discovered penicillin?", "options": ["Curie", "Fleming", "Pasteur", "Koch"], "answer": 1},
        {"q": "The ancient Olympics were held in which country?", "options": ["Italy", "Greece", "Egypt", "Turkey"], "answer": 1},
        {"q": "Who wrote the Declaration of Independence?", "options": ["Jefferson", "Franklin", "Adams", "Hamilton"], "answer": 0},
        {"q": "Which empire was ruled by Julius Caesar?", "options": ["Greek", "Persian", "Roman", "Egyptian"], "answer": 2},
        {"q": "The Wright brothers invented the:", "options": ["Telephone", "Airplane", "Car", "Radio"], "answer": 1},
    ],
    "Geography": [
        {"q": "What is the longest river in the world?", "options": ["Amazon", "Nile", "Yangtze", "Mississippi"], "answer": 1},
        {"q": "Which country has the most natural lakes?", "options": ["USA", "Russia", "Canada", "China"], "answer": 2},
        {"q": "What is the smallest country in the world?", "options": ["Monaco", "San Marino", "Vatican City", "Malta"], "answer": 2},
        {"q": "Which desert is the largest (non-polar)?", "options": ["Gobi", "Sahara", "Kalahari", "Atacama"], "answer": 1},
        {"q": "Mount Everest is located in which mountain range?", "options": ["Andes", "Rockies", "Himalayas", "Alps"], "answer": 2},
        {"q": "Which ocean is the deepest?", "options": ["Atlantic", "Indian", "Arctic", "Pacific"], "answer": 3},
        {"q": "What is the capital of Japan?", "options": ["Beijing", "Seoul", "Tokyo", "Bangkok"], "answer": 2},
        {"q": "Which European country is known as the Land of a Thousand Lakes?", "options": ["Sweden", "Norway", "Finland", "Iceland"], "answer": 2},
        {"q": "The Amazon rainforest is mostly located in which country?", "options": ["Peru", "Colombia", "Brazil", "Venezuela"], "answer": 2},
        {"q": "Which African country was formerly known as Abyssinia?", "options": ["Ethiopia", "Eritrea", "Sudan", "Somalia"], "answer": 0},
    ],
    "Entertainment": [
        {"q": "Who played Jack Dawson in Titanic?", "options": ["Brad Pitt", "Leonardo DiCaprio", "Matt Damon", "Johnny Depp"], "answer": 1},
        {"q": "Which band performed 'Bohemian Rhapsody'?", "options": ["The Beatles", "Queen", "Led Zeppelin", "Pink Floyd"], "answer": 1},
        {"q": "What is the name of Harry Potter's owl?", "options": ["Hedwig", "Errol", "Pigwidgeon", "Hermes"], "answer": 0},
        {"q": "Who directed 'Inception'?", "options": ["Spielberg", "Nolan", "Tarantino", "Cameron"], "answer": 1},
        {"q": "Which game features the character 'Master Chief'?", "options": ["Call of Duty", "Halo", "Gears of War", "Destiny"], "answer": 1},
        {"q": "Who is the singer of 'Rolling in the Deep'?", "options": ["Adele", "Beyoncé", "Lady Gaga", "Rihanna"], "answer": 0},
        {"q": "Which movie won the Oscar for Best Picture in 2020?", "options": ["1917", "Joker", "Parasite", "Once Upon a Time in Hollywood"], "answer": 2},
        {"q": "What is the name of the dragon in The Hobbit?", "options": ["Smaug", "Drogon", "Toothless", "Norbert"], "answer": 0},
        {"q": "Who created the TV series 'The Simpsons'?", "options": ["Seth MacFarlane", "Matt Groening", "Mike Judge", "Trey Parker"], "answer": 1},
        {"q": "Which actor played Iron Man?", "options": ["Chris Evans", "Chris Hemsworth", "Robert Downey Jr.", "Scarlett Johansson"], "answer": 2},
    ]
}

class QuizGame:
    def __init__(self):
        self.categories = list(QUESTIONS.keys())
        self.current_category = 0
        self.current_q_index = 0
        self.questions = None
        self.score = 0
        self.highscore = self.load_highscore()
        self.game_over = False
        self.category_selection = True   # Start in category selection mode
        self.waiting_for_next = False
        self.next_timer = 0
        self.time_left = 10
        self.timer_start = 0
        self.showing_feedback = False
        self.feedback_text = ""
        self.feedback_color = WHITE
        self.feedback_timer = 0
        self.selected_option = -1
        self.answer_correct = False

        # UI
        self.category_buttons = []
        self.create_category_buttons()

    def load_highscore(self):
        try:
            with open("quiz_highscore.json", "r") as f:
                data = json.load(f)
                return data.get("highscore", 0)
        except:
            return 0

    def save_highscore(self):
        if self.score > self.highscore:
            self.highscore = self.score
            with open("quiz_highscore.json", "w") as f:
                json.dump({"highscore": self.highscore}, f)

    def create_category_buttons(self):
        button_width = 180
        button_height = 50
        start_x = (WIDTH - (len(self.categories) * (button_width + 20))) // 2
        start_y = 150
        for i, cat in enumerate(self.categories):
            rect = pygame.Rect(start_x + i * (button_width + 20), start_y, button_width, button_height)
            self.category_buttons.append((rect, cat, i))

    def start_quiz(self, category_index):
        self.current_category = category_index
        self.questions = QUESTIONS[self.categories[category_index]]
        self.current_q_index = 0
        self.score = 0
        self.game_over = False
        self.category_selection = False   # Now playing
        self.waiting_for_next = False
        self.showing_feedback = False
        self.time_left = 10
        self.timer_start = pygame.time.get_ticks()
        self.selected_option = -1
        self.load_question()

    def load_question(self):
        if self.current_q_index >= len(self.questions):
            self.end_game()
            return
        self.time_left = 10
        self.timer_start = pygame.time.get_ticks()
        self.selected_option = -1
        self.showing_feedback = False
        self.waiting_for_next = False

    def end_game(self):
        self.game_over = True
        self.category_selection = False
        if self.score > self.highscore:
            self.highscore = self.score
            self.save_highscore()

    def check_answer(self, option_index):
        if self.showing_feedback or self.waiting_for_next or self.category_selection:
            return
        correct = (option_index == self.questions[self.current_q_index]["answer"])
        self.selected_option = option_index
        self.answer_correct = correct

        if correct:
            points = int(self.time_left * 10) + 10
            self.score += points
            self.feedback_text = f"Correct! +{points} points"
            self.feedback_color = GREEN
        else:
            correct_ans = self.questions[self.current_q_index]["options"][self.questions[self.current_q_index]["answer"]]
            self.feedback_text = f"Wrong! Correct answer: {correct_ans}"
            self.feedback_color = RED

        self.showing_feedback = True
        self.feedback_timer = 60   # 1 second at 60 fps
        self.waiting_for_next = True
        self.next_timer = 90       # 1.5 seconds

    def update(self):
        if self.game_over or self.category_selection:
            return
        if self.waiting_for_next:
            if self.next_timer > 0:
                self.next_timer -= 1
            else:
                self.waiting_for_next = False
                self.current_q_index += 1
                if self.current_q_index < len(self.questions):
                    self.load_question()
                else:
                    self.end_game()
            return

        # update timer
        elapsed = (pygame.time.get_ticks() - self.timer_start) / 1000.0
        self.time_left = max(0, 10 - elapsed)
        if self.time_left <= 0 and not self.showing_feedback and not self.waiting_for_next:
            self.check_answer(-1)   # time's up, treat as wrong

        if self.showing_feedback:
            if self.feedback_timer > 0:
                self.feedback_timer -= 1
            else:
                self.showing_feedback = False

    def draw(self, surf):
        surf.fill(BLACK)

        # Game over screen
        if self.game_over:
            title = font_large.render("QUIZ COMPLETE", True, YELLOW)
            score_text = font_medium.render(f"Your Score: {self.score}", True, WHITE)
            high_text = font_medium.render(f"High Score: {self.highscore}", True, GREEN)
            restart_text = font_small.render("Press R to restart, Q to quit", True, WHITE)
            surf.blit(title, (WIDTH//2 - title.get_width()//2, 150))
            surf.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 250))
            surf.blit(high_text, (WIDTH//2 - high_text.get_width()//2, 300))
            surf.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 400))
            return

        # Category selection screen
        if self.category_selection:
            title = font_large.render("Choose a Category", True, WHITE)
            surf.blit(title, (WIDTH//2 - title.get_width()//2, 80))
            for rect, cat, idx in self.category_buttons:
                pygame.draw.rect(surf, BLUE, rect)
                pygame.draw.rect(surf, WHITE, rect, 2)
                text = font_medium.render(cat, True, WHITE)
                text_rect = text.get_rect(center=rect.center)
                surf.blit(text, text_rect)
            return

        # Quiz playing screen
        q_data = self.questions[self.current_q_index]
        # Question text wrapping
        question_surf = font_medium.render(q_data["q"], True, WHITE)
        if question_surf.get_width() > WIDTH - 40:
            question_surf = font_small.render(q_data["q"], True, WHITE)
        surf.blit(question_surf, (WIDTH//2 - question_surf.get_width()//2, 80))

        # Timer bar
        timer_width = int((self.time_left / 10) * (WIDTH - 100))
        pygame.draw.rect(surf, GRAY, (50, 130, WIDTH-100, 20))
        pygame.draw.rect(surf, GREEN if self.time_left > 3 else RED, (50, 130, timer_width, 20))

        # Score
        score_surf = font_small.render(f"Score: {self.score}", True, YELLOW)
        surf.blit(score_surf, (20, 20))

        # Options
        option_height = 60
        start_y = 180
        for i, opt in enumerate(q_data["options"]):
            rect = pygame.Rect(100, start_y + i * (option_height + 10), WIDTH-200, option_height)
            color = BLUE
            if self.selected_option == i:
                color = GREEN if self.answer_correct else RED
            elif self.showing_feedback and i == q_data["answer"]:
                color = GREEN
            pygame.draw.rect(surf, color, rect)
            pygame.draw.rect(surf, WHITE, rect, 2)
            opt_text = font_medium.render(opt, True, WHITE)
            opt_rect = opt_text.get_rect(center=rect.center)
            surf.blit(opt_text, opt_rect)

        # Feedback message
        if self.showing_feedback:
            fb_surf = font_medium.render(self.feedback_text, True, self.feedback_color)
            fb_rect = fb_surf.get_rect(center=(WIDTH//2, HEIGHT - 80))
            surf.blit(fb_surf, fb_rect)

        # Next question hint
        if self.waiting_for_next:
            next_surf = font_small.render("Next question...", True, WHITE)
            surf.blit(next_surf, (WIDTH//2 - next_surf.get_width()//2, HEIGHT - 120))

def main():
    game = QuizGame()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.game_over:
                    # For game over, restart handled by keyboard
                    pass
                elif game.category_selection:
                    # Click on category buttons
                    pos = pygame.mouse.get_pos()
                    for rect, cat, idx in game.category_buttons:
                        if rect.collidepoint(pos):
                            game.start_quiz(idx)
                            break
                else:
                    # Click on answer options (only if not in feedback/waiting)
                    if not game.waiting_for_next and not game.showing_feedback:
                        option_height = 60
                        start_y = 180
                        for i in range(4):
                            rect = pygame.Rect(100, start_y + i * (option_height + 10), WIDTH-200, option_height)
                            if rect.collidepoint(pos):
                                game.check_answer(i)
                                break
            if event.type == pygame.KEYDOWN:
                if game.game_over:
                    if event.key == pygame.K_r:
                        game = QuizGame()  # fresh restart
                    elif event.key == pygame.K_q:
                        running = False
                # Optional: add key shortcuts for answers (1-4)
                if not game.category_selection and not game.game_over and not game.waiting_for_next and not game.showing_feedback:
                    if event.key == pygame.K_1:
                        game.check_answer(0)
                    elif event.key == pygame.K_2:
                        game.check_answer(1)
                    elif event.key == pygame.K_3:
                        game.check_answer(2)
                    elif event.key == pygame.K_4:
                        game.check_answer(3)

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()