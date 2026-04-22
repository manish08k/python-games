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

# Shapes and their rotations (matrices)
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
    'I': (0, 255, 255),   # Cyan
    'O': (255, 255, 0),   # Yellow
    'T': (128, 0, 128),   # Purple
    'S': (0, 255, 0),     # Green
    'Z': (255, 0, 0),     # Red
    'J': (0, 0, 255),     # Blue
    'L': (255, 165, 0)    # Orange
}

# Scoring: lines cleared -> points
SCORES = {1: 100, 2: 300, 3: 500, 4: 800}


# ---------- PIECE CLASS ----------
class Piece:
    def __init__(self, shape_name):
        self.shape_name = shape_name
        self.matrix = [row[:] for row in SHAPES[shape_name]]  # deep copy
        self.color = COLORS[shape_name]
        self.x = 5 - len(self.matrix[0]) // 2   # centre horizontally
        self.y = 0                               # top of grid

    def rotate(self):
        """Rotate clockwise (matrix transpose + reverse rows)."""
        rotated = [list(row) for row in zip(*self.matrix[::-1])]
        return rotated


# ---------- GRID CLASS ----------
class Grid:
    def __init__(self):
        self.rows = 20
        self.cols = 10
        self.grid = [[(0, 0, 0) for _ in range(self.cols)] for _ in range(self.rows)]
        # Locked pieces store their colour

    def is_valid_position(self, piece, offset_x=0, offset_y=0, matrix=None):
        """Check if piece (with optional offsets and custom matrix) fits on the grid."""
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
        """Copy piece colour into the grid at its current position."""
        for r in range(len(piece.matrix)):
            for c in range(len(piece.matrix[0])):
                if piece.matrix[r][c] != 0:
                    self.grid[piece.y + r][piece.x + c] = piece.color

    def clear_lines(self):
        """Remove full rows, shift above rows down, return number of lines cleared."""
        lines_cleared = 0
        y = self.rows - 1
        while y >= 0:
            if all(self.grid[y][x] != (0, 0, 0) for x in range(self.cols)):
                # Remove row
                del self.grid[y]
                self.grid.insert(0, [(0, 0, 0) for _ in range(self.cols)])
                lines_cleared += 1
                # Stay on same y index because rows shifted down
            else:
                y -= 1
        return lines_cleared


# ---------- GAME CLASS ----------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 30)
        self.small_font = pygame.font.SysFont('Arial', 20)

        self.reset_game()

    def reset_game(self):
        """Reset all game state variables for a new game."""
        self.grid = Grid()
        self.current_piece = self._get_random_piece()
        self.next_piece = self._get_random_piece()
        self.score = 0
        self.level = 1
        self.lines_cleared_total = 0
        self.fall_time = 0
        self.fall_speed = 500  # milliseconds per cell
        self.game_over = False
        self.state = "START"   # "START", "PLAYING", "GAME_OVER"

    def _get_random_piece(self):
        return Piece(random.choice(list(SHAPES.keys())))

    def _calculate_fall_speed(self):
        """Return fall delay in milliseconds based on level."""
        # Classic Tetris speed: level 1 = 500ms, each level reduces by ~33ms, min 100ms
        return max(100, 500 - (self.level - 1) * 33)

    def _handle_input(self):
        keys = pygame.key.get_pressed()
        if self.state == "PLAYING":
            if keys[pygame.K_LEFT]:
                self._move_piece(-1, 0)
            if keys[pygame.K_RIGHT]:
                self._move_piece(1, 0)
            if keys[pygame.K_DOWN]:
                self._move_piece(0, 1)
            if keys[pygame.K_SPACE]:
                self._hard_drop()
            if keys[pygame.K_UP]:
                self._rotate_piece()

    def _move_piece(self, dx, dy):
        if self.grid.is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        elif dy == 1:  # Moving down and collision -> lock piece
            self._lock_and_spawn()
        return False

    def _rotate_piece(self):
        rotated_matrix = self.current_piece.rotate()
        # Simple wall kicks: try original position, then left shift, then right shift
        offsets = [0, -1, 1, -2, 2]  # basic kick attempts
        for offset in offsets:
            if self.grid.is_valid_position(self.current_piece, offset_x=offset, matrix=rotated_matrix):
                self.current_piece.matrix = rotated_matrix
                self.current_piece.x += offset
                return
        # No valid rotation found

    def _hard_drop(self):
        while self.grid.is_valid_position(self.current_piece, 0, 1):
            self.current_piece.y += 1
        self._lock_and_spawn()

    def _lock_and_spawn(self):
        """Lock current piece, clear lines, update score/level, spawn next piece."""
        self.grid.lock_piece(self.current_piece)
        lines = self.grid.clear_lines()
        self._update_score_and_level(lines)

        # Spawn next piece
        self.current_piece = self.next_piece
        self.next_piece = self._get_random_piece()

        # If spawn position is invalid -> Game Over
        if not self.grid.is_valid_position(self.current_piece):
            self.state = "GAME_OVER"

    def _update_score_and_level(self, lines_cleared):
        if lines_cleared > 0:
            self.score += SCORES[lines_cleared]
            self.lines_cleared_total += lines_cleared
            self.level = 1 + self.lines_cleared_total // 10
            self.fall_speed = self._calculate_fall_speed()

    def _draw_grid(self):
        """Draw the playfield grid lines and locked blocks."""
        # Draw locked blocks
        for r in range(self.grid.rows):
            for c in range(self.grid.cols):
                colour = self.grid.grid[r][c]
                if colour != (0, 0, 0):
                    pygame.draw.rect(self.screen, colour,
                                     (TOP_LEFT_X + c * BLOCK_SIZE,
                                      TOP_LEFT_Y + r * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(self.screen, (50, 50, 50),
                                     (TOP_LEFT_X + c * BLOCK_SIZE,
                                      TOP_LEFT_Y + r * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE), 1)
                else:
                    # Draw grid lines only
                    pygame.draw.rect(self.screen, (40, 40, 40),
                                     (TOP_LEFT_X + c * BLOCK_SIZE,
                                      TOP_LEFT_Y + r * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE), 1)

        # Draw current piece (if playing)
        if self.state == "PLAYING" and self.current_piece:
            piece = self.current_piece
            for r in range(len(piece.matrix)):
                for c in range(len(piece.matrix[0])):
                    if piece.matrix[r][c] != 0:
                        pygame.draw.rect(self.screen, piece.color,
                                         (TOP_LEFT_X + (piece.x + c) * BLOCK_SIZE,
                                          TOP_LEFT_Y + (piece.y + r) * BLOCK_SIZE,
                                          BLOCK_SIZE, BLOCK_SIZE))
                        pygame.draw.rect(self.screen, (255, 255, 255),
                                         (TOP_LEFT_X + (piece.x + c) * BLOCK_SIZE,
                                          TOP_LEFT_Y + (piece.y + r) * BLOCK_SIZE,
                                          BLOCK_SIZE, BLOCK_SIZE), 1)

    def _draw_ui(self):
        """Draw score, level, next piece preview."""
        # Score and Level
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        level_text = self.font.render(f"Level: {self.level}", True, (255, 255, 255))
        self.screen.blit(score_text, (TOP_LEFT_X + PLAY_WIDTH + 20, TOP_LEFT_Y + 50))
        self.screen.blit(level_text, (TOP_LEFT_X + PLAY_WIDTH + 20, TOP_LEFT_Y + 100))

        # Next piece label
        next_label = self.small_font.render("Next:", True, (200, 200, 200))
        self.screen.blit(next_label, (TOP_LEFT_X + PLAY_WIDTH + 20, TOP_LEFT_Y + 180))

        # Draw next piece
        if self.next_piece:
            piece = self.next_piece
            start_x = TOP_LEFT_X + PLAY_WIDTH + 30
            start_y = TOP_LEFT_Y + 220
            for r in range(len(piece.matrix)):
                for c in range(len(piece.matrix[0])):
                    if piece.matrix[r][c] != 0:
                        pygame.draw.rect(self.screen, piece.color,
                                         (start_x + c * BLOCK_SIZE,
                                          start_y + r * BLOCK_SIZE,
                                          BLOCK_SIZE, BLOCK_SIZE))
                        pygame.draw.rect(self.screen, (255, 255, 255),
                                         (start_x + c * BLOCK_SIZE,
                                          start_y + r * BLOCK_SIZE,
                                          BLOCK_SIZE, BLOCK_SIZE), 1)

    def _draw_start_screen(self):
        self.screen.fill((0, 0, 0))
        title = self.font.render("TETRIS", True, (255, 255, 0))
        press = self.small_font.render("Press any key to start", True, (200, 200, 200))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(press, (SCREEN_WIDTH//2 - press.get_width()//2, SCREEN_HEIGHT//2))
        pygame.display.update()

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
        # Draw border around play area
        pygame.draw.rect(self.screen, (100, 100, 100),
                         (TOP_LEFT_X - 2, TOP_LEFT_Y - 2, PLAY_WIDTH + 4, PLAY_HEIGHT + 4), 2)
        self._draw_grid()
        self._draw_ui()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60)  # 60 FPS
            self.fall_time += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.state == "START":
                    if event.type == pygame.KEYDOWN:
                        self.state = "PLAYING"
                        self.reset_game()

                elif self.state == "GAME_OVER":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.reset_game()
                            self.state = "PLAYING"
                        elif event.key == pygame.K_q:
                            running = False

                elif self.state == "PLAYING":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self._rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            self._hard_drop()

            # Continuous key handling (left/right/down)
            self._handle_input()

            # Automatic falling
            if self.state == "PLAYING" and not self.game_over:
                if self.fall_time >= self.fall_speed:
                    self.fall_time = 0
                    self._move_piece(0, 1)

            # Render based on state
            if self.state == "START":
                self._draw_start_screen()
            elif self.state == "PLAYING":
                self._draw_playing()
                pygame.display.update()
            elif self.state == "GAME_OVER":
                self._draw_playing()  # Show grid behind overlay
                self._draw_game_over_screen()

        pygame.quit()


# ---------- ENTRY POINT ----------
if __name__ == "__main__":
    game = Game()
    game.run()