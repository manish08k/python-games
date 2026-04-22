import pygame
import random

# ---------- CONSTANTS ----------
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600
PLAY_WIDTH = 300   # 10 columns * 30 px
PLAY_HEIGHT = 600  # 20 rows * 30 px
BLOCK_SIZE = 30

TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT

# Shapes and rotations
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'T': [[0, 1, 0],
          [1, 1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]],
    'Z': [[1, 1, 0],
          [0, 1, 1]],
    'J': [[1, 0, 0],
          [1, 1, 1]],
    'L': [[0, 0, 1],
          [1, 1, 1]]
}

COLORS = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (128, 0, 128),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'J': (0, 0, 255),
    'L': (255, 165, 0)
}

SCORES = {1: 100, 2: 300, 3: 500, 4: 800}


class Piece:
    def __init__(self, shape_name):
        self.shape_name = shape_name
        self.matrix = [row[:] for row in SHAPES[shape_name]]
        self.color = COLORS[shape_name]
        self.x = 5 - len(self.matrix[0]) // 2
        self.y = 0

    def rotate(self):
        return [list(row) for row in zip(*self.matrix[::-1])]


class Grid:
    def __init__(self):
        self.rows = 20
        self.cols = 10
        self.grid = [[(0, 0, 0) for _ in range(self.cols)] for _ in range(self.rows)]

    def is_valid_position(self, piece, offset_x=0, offset_y=0, matrix=None):
        if matrix is None:
            matrix = piece.matrix
        for r in range(len(matrix)):
            for c in range(len(matrix[0])):
                if matrix[r][c] != 0:
                    x = piece.x + c + offset_x
                    y = piece.y + r + offset_y
                    if x < 0 or x >= self.cols or y >= self.rows:
                        return False
                    if y >= 0 and self.grid[y][x] != (0, 0, 0):
                        return False
        return True

    def lock_piece(self, piece):
        for r in range(len(piece.matrix)):
            for c in range(len(piece.matrix[0])):
                if piece.matrix[r][c] != 0:
                    self.grid[piece.y + r][piece.x + c] = piece.color

    def clear_lines(self):
        lines_cleared = 0
        y = self.rows - 1
        while y >= 0:
            if all(self.grid[y][x] != (0, 0, 0) for x in range(self.cols)):
                del self.grid[y]
                self.grid.insert(0, [(0, 0, 0) for _ in range(self.cols)])
                lines_cleared += 1
            else:
                y -= 1
        return lines_cleared


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 30)
        self.small_font = pygame.font.SysFont('Arial', 20)

        # Disable key repeat to get exactly one move per press
        pygame.key.set_repeat(0)

        # 7-bag randomizer
        self.piece_bag = []
        self.refill_bag()

        self.reset_game()
        self.state = "PLAYING"

    def refill_bag(self):
        """Refill the bag with all 7 pieces in random order."""
        self.piece_bag = list(SHAPES.keys())
        random.shuffle(self.piece_bag)

    def get_next_piece_from_bag(self):
        """Return a piece name using the 7-bag system."""
        if not self.piece_bag:
            self.refill_bag()
        return self.piece_bag.pop()

    def _get_random_piece(self):
        """Create a Piece using the 7-bag randomizer."""
        return Piece(self.get_next_piece_from_bag())

    def reset_game(self):
        self.grid = Grid()
        self.current_piece = self._get_random_piece()
        self.next_piece = self._get_random_piece()
        self.score = 0
        self.level = 1
        self.lines_cleared_total = 0
        self.fall_time = 0
        self.fall_speed = self._calculate_fall_speed()
        self.game_over = False

    def _calculate_fall_speed(self):
        return max(100, 500 - (self.level - 1) * 33)

    def _move_piece(self, dx, dy):
        if self.grid.is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        elif dy == 1:  # moving down & collision -> lock
            self._lock_and_spawn()
        return False

    def _rotate_piece(self):
        rotated_matrix = self.current_piece.rotate()
        for offset in [0, -1, 1, -2, 2]:
            if self.grid.is_valid_position(self.current_piece, offset_x=offset, matrix=rotated_matrix):
                self.current_piece.matrix = rotated_matrix
                self.current_piece.x += offset
                return

    def _hard_drop(self):
        while self.grid.is_valid_position(self.current_piece, 0, 1):
            self.current_piece.y += 1
        self._lock_and_spawn()

    def _lock_and_spawn(self):
        self.grid.lock_piece(self.current_piece)
        lines = self.grid.clear_lines()
        self._update_score_and_level(lines)

        self.current_piece = self.next_piece
        self.next_piece = self._get_random_piece()

        if not self.grid.is_valid_position(self.current_piece):
            self.game_over = True

    def _update_score_and_level(self, lines_cleared):
        if lines_cleared > 0:
            self.score += SCORES[lines_cleared]
            self.lines_cleared_total += lines_cleared
            self.level = 1 + self.lines_cleared_total // 10
            self.fall_speed = self._calculate_fall_speed()

    def _draw_grid(self):
        # Locked blocks
        for r in range(self.grid.rows):
            for c in range(self.grid.cols):
                colour = self.grid.grid[r][c]
                rect = pygame.Rect(TOP_LEFT_X + c * BLOCK_SIZE,
                                   TOP_LEFT_Y + r * BLOCK_SIZE,
                                   BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(self.screen, colour, rect)
                pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)

        # Current piece
        if self.current_piece:
            piece = self.current_piece
            for r in range(len(piece.matrix)):
                for c in range(len(piece.matrix[0])):
                    if piece.matrix[r][c]:
                        rect = pygame.Rect(TOP_LEFT_X + (piece.x + c) * BLOCK_SIZE,
                                           TOP_LEFT_Y + (piece.y + r) * BLOCK_SIZE,
                                           BLOCK_SIZE, BLOCK_SIZE)
                        pygame.draw.rect(self.screen, piece.color, rect)
                        pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)

    def _draw_ui(self):
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        level_text = self.font.render(f"Level: {self.level}", True, (255, 255, 255))
        self.screen.blit(score_text, (TOP_LEFT_X + PLAY_WIDTH + 20, TOP_LEFT_Y + 50))
        self.screen.blit(level_text, (TOP_LEFT_X + PLAY_WIDTH + 20, TOP_LEFT_Y + 100))

        next_label = self.small_font.render("Next:", True, (200, 200, 200))
        self.screen.blit(next_label, (TOP_LEFT_X + PLAY_WIDTH + 20, TOP_LEFT_Y + 180))

        if self.next_piece:
            piece = self.next_piece
            start_x = TOP_LEFT_X + PLAY_WIDTH + 30
            start_y = TOP_LEFT_Y + 220
            for r in range(len(piece.matrix)):
                for c in range(len(piece.matrix[0])):
                    if piece.matrix[r][c]:
                        rect = pygame.Rect(start_x + c * BLOCK_SIZE,
                                           start_y + r * BLOCK_SIZE,
                                           BLOCK_SIZE, BLOCK_SIZE)
                        pygame.draw.rect(self.screen, piece.color, rect)
                        pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)

    def _draw_game_over_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        go_text = self.font.render("GAME OVER", True, (255, 0, 0))
        score_text = self.small_font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        restart_text = self.small_font.render("Press R to Restart or Q to Quit", True, (200, 200, 200))

        self.screen.blit(go_text, (SCREEN_WIDTH//2 - go_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 20))
        self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        pygame.display.update()

    def _draw_playing(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (100, 100, 100),
                         (TOP_LEFT_X - 2, TOP_LEFT_Y - 2, PLAY_WIDTH + 4, PLAY_HEIGHT + 4), 2)
        self._draw_grid()
        self._draw_ui()
        pygame.display.update()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60)
            self.fall_time += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.game_over:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.reset_game()
                            self.game_over = False
                        elif event.key == pygame.K_q:
                            running = False
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            self._move_piece(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self._move_piece(1, 0)
                        elif event.key == pygame.K_DOWN:
                            self._move_piece(0, 1)
                        elif event.key == pygame.K_UP:
                            self._rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            self._hard_drop()

            # Automatic falling (gravity)
            if not self.game_over:
                if self.fall_time >= self.fall_speed:
                    self.fall_time = 0
                    self._move_piece(0, 1)

            # Render
            self._draw_playing()
            if self.game_over:
                self._draw_game_over_screen()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()