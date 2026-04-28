import pygame
import sys
import math
import random

pygame.init()

# Constants
SCREEN_WIDTH = 560
SCREEN_HEIGHT = 620
CELL_SIZE = 20
COLS = 28
ROWS = 31

BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (33, 33, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)
DARK_BLUE = (0, 0, 139)
GRAY = (128, 128, 128)

# Maze layout (0=path, 1=wall, 2=dot, 3=power pellet, 4=ghost house)
MAZE = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,3,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,3,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
    [1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,1,1,1,1,1],
    [1,1,1,1,1,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,1,1,1,1,1],
    [1,1,1,1,1,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,1,1,1,1,1],
    [1,1,1,1,1,1,2,1,1,0,1,1,1,4,4,1,1,1,0,1,1,2,1,1,1,1,1,1],
    [1,1,1,1,1,1,2,1,1,0,1,4,4,4,4,4,4,1,0,1,1,2,1,1,1,1,1,1],
    [0,0,0,0,0,0,2,0,0,0,1,4,4,4,4,4,4,1,0,0,0,2,0,0,0,0,0,0],
    [1,1,1,1,1,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,1,1,1,1,1],
    [1,1,1,1,1,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,1,1,1,1,1],
    [1,1,1,1,1,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,1,1,1,1,1],
    [1,1,1,1,1,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,3,2,2,1,1,2,2,2,2,2,2,2,0,0,2,2,2,2,2,2,2,1,1,2,2,3,1],
    [1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1],
    [1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1],
    [1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,1,2,1],
    [1,2,1,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

class PacMan:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = 14 * CELL_SIZE
        self.y = 23 * CELL_SIZE
        self.dx = 0
        self.dy = 0
        self.next_dx = 0
        self.next_dy = 0
        self.speed = 2
        self.mouth_angle = 45
        self.mouth_dir = 1
        self.alive = True
        self.death_frame = 0
        self.dying = False

    def draw(self, screen):
        cx = int(self.x + CELL_SIZE // 2)
        cy = int(self.y + CELL_SIZE // 2)
        r = CELL_SIZE // 2 - 1

        if self.dying:
            angle = self.death_frame * 6
            if angle < 180:
                pygame.draw.arc(screen, YELLOW,
                    (cx - r, cy - r, r * 2, r * 2),
                    math.radians(angle), math.radians(360 - angle), r)
                pygame.draw.circle(screen, YELLOW, (cx, cy), r // 2)
            return

        # Direction angle
        if self.dx == 1: base = 0
        elif self.dx == -1: base = 180
        elif self.dy == -1: base = 90
        elif self.dy == 1: base = 270
        else: base = 0

        start_angle = math.radians(base + self.mouth_angle)
        end_angle = math.radians(base + 360 - self.mouth_angle)

        pygame.draw.circle(screen, YELLOW, (cx, cy), r)
        if self.mouth_angle > 2:
            points = [(cx, cy)]
            for a in range(int(math.degrees(start_angle)), int(math.degrees(end_angle)) + 1, 5):
                px = cx + r * math.cos(math.radians(a))
                py = cy - r * math.sin(math.radians(a))
                points.append((px, py))
            if len(points) > 2:
                pygame.draw.polygon(screen, BLACK, points)

    def update(self, maze):
        if self.dying:
            self.death_frame += 1
            return

        self.mouth_angle += self.mouth_dir * 3
        if self.mouth_angle >= 45 or self.mouth_angle <= 0:
            self.mouth_dir *= -1

        # Try next direction
        nx = self.x + self.next_dx * self.speed
        ny = self.y + self.next_dy * self.speed
        if not self.collides(nx, ny, maze):
            self.dx = self.next_dx
            self.dy = self.next_dy

        nx = self.x + self.dx * self.speed
        ny = self.y + self.dy * self.speed
        if not self.collides(nx, ny, maze):
            self.x = nx
            self.y = ny
        else:
            # Snap to grid
            self.x = round(self.x / CELL_SIZE) * CELL_SIZE
            self.y = round(self.y / CELL_SIZE) * CELL_SIZE

        # Tunnel wrap
        if self.x < -CELL_SIZE:
            self.x = COLS * CELL_SIZE
        elif self.x > COLS * CELL_SIZE:
            self.x = -CELL_SIZE

    def collides(self, nx, ny, maze):
        corners = [
            (nx + 2, ny + 2),
            (nx + CELL_SIZE - 3, ny + 2),
            (nx + 2, ny + CELL_SIZE - 3),
            (nx + CELL_SIZE - 3, ny + CELL_SIZE - 3),
        ]
        for cx, cy in corners:
            col = int(cx // CELL_SIZE)
            row = int(cy // CELL_SIZE)
            if 0 <= row < ROWS and 0 <= col < COLS:
                if maze[row][col] == 1:
                    return True
        return False

    def get_cell(self):
        return int((self.y + CELL_SIZE // 2) // CELL_SIZE), int((self.x + CELL_SIZE // 2) // CELL_SIZE)


class Ghost:
    COLORS = [RED, PINK, CYAN, ORANGE]
    NAMES = ['blinky', 'pinky', 'inky', 'clyde']

    def __init__(self, index):
        self.index = index
        self.color = self.COLORS[index]
        self.name = self.NAMES[index]
        self.reset()

    def reset(self):
        self.x = (12 + self.index % 2 * 2) * CELL_SIZE
        self.y = (13 + self.index // 2) * CELL_SIZE
        self.dx = 0
        self.dy = -1
        self.speed = 1.5
        self.frightened = False
        self.frighten_timer = 0
        self.eaten = False
        self.out_of_house = self.index == 0
        self.house_timer = self.index * 60

    def draw(self, screen):
        cx = int(self.x + CELL_SIZE // 2)
        cy = int(self.y + CELL_SIZE // 2)
        r = CELL_SIZE // 2 - 1

        if self.eaten:
            # Draw eyes only
            pygame.draw.circle(screen, WHITE, (cx - 3, cy - 2), 3)
            pygame.draw.circle(screen, WHITE, (cx + 3, cy - 2), 3)
            pygame.draw.circle(screen, BLUE, (cx - 3, cy - 2), 2)
            pygame.draw.circle(screen, BLUE, (cx + 3, cy - 2), 2)
            return

        color = (0, 0, 255) if self.frightened else self.color
        if self.frightened and self.frighten_timer < 120 and (self.frighten_timer // 15) % 2 == 0:
            color = WHITE

        # Body
        pygame.draw.circle(screen, color, (cx, cy - 2), r)
        pygame.draw.rect(screen, color, (cx - r, cy - 2, r * 2, r + 2))

        # Wavy bottom
        wave_y = cy + r
        for i in range(4):
            wx = cx - r + i * (r // 2)
            pygame.draw.circle(screen, BLACK, (wx + r // 4, wave_y), r // 4)

        # Eyes
        pygame.draw.circle(screen, WHITE, (cx - 3, cy - 4), 3)
        pygame.draw.circle(screen, WHITE, (cx + 3, cy - 4), 3)
        if not self.frightened:
            ex = cx - 3 + self.dx
            ey = cy - 4 + self.dy
            pygame.draw.circle(screen, DARK_BLUE, (ex, ey), 2)
            ex = cx + 3 + self.dx
            pygame.draw.circle(screen, DARK_BLUE, (ex, ey), 2)

    def update(self, maze, pacman):
        if not self.out_of_house:
            self.house_timer -= 1
            if self.house_timer <= 0:
                self.out_of_house = True
                self.x = 14 * CELL_SIZE
                self.y = 11 * CELL_SIZE
            return

        if self.eaten:
            # Return to house
            target_r, target_c = 13, 14
            self.move_toward(target_r, target_c, maze)
            gr, gc = self.get_cell()
            if gr == target_r and gc == target_c:
                self.eaten = False
                self.frightened = False
            return

        if self.frightened:
            self.frighten_timer -= 1
            if self.frighten_timer <= 0:
                self.frightened = False

        pr, pc = pacman.get_cell()

        if self.frightened:
            # Random movement
            self.random_move(maze)
        else:
            if self.name == 'blinky':
                self.move_toward(pr, pc, maze)
            elif self.name == 'pinky':
                self.move_toward(pr + 4 * pacman.dy, pc + 4 * pacman.dx, maze)
            elif self.name == 'inky':
                self.move_toward(pr + 2, pc + 2, maze)
            elif self.name == 'clyde':
                gr, gc = self.get_cell()
                dist = math.hypot(gr - pr, gc - pc)
                if dist > 8:
                    self.move_toward(pr, pc, maze)
                else:
                    self.move_toward(ROWS - 2, 0, maze)

        # Tunnel
        if self.x < -CELL_SIZE:
            self.x = COLS * CELL_SIZE
        elif self.x > COLS * CELL_SIZE:
            self.x = -CELL_SIZE

    def move_toward(self, target_r, target_c, maze):
        gr, gc = self.get_cell()
        best_dir = None
        best_dist = float('inf')
        opposite = (-self.dy, -self.dx)

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if (dr, dc) == opposite:
                continue
            nr, nc = gr + dr, gc + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] != 1:
                dist = math.hypot(nr - target_r, nc - target_c)
                if dist < best_dist:
                    best_dist = dist
                    best_dir = (dr, dc)

        if best_dir:
            self.move_in_dir(best_dir[0], best_dir[1], maze)

    def random_move(self, maze):
        gr, gc = self.get_cell()
        opposite = (-self.dy, -self.dx)
        options = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if (dr, dc) == opposite:
                continue
            nr, nc = gr + dr, gc + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] != 1:
                options.append((dr, dc))
        if options:
            dr, dc = random.choice(options)
            self.move_in_dir(dr, dc, maze)

    def move_in_dir(self, dr, dc, maze):
        self.dy = dr
        self.dx = dc
        tx = self.x + dc * self.speed
        ty = self.y + dr * self.speed
        if not self.ghost_collides(tx, ty, maze):
            self.x = tx
            self.y = ty
        else:
            self.x = round(self.x / CELL_SIZE) * CELL_SIZE
            self.y = round(self.y / CELL_SIZE) * CELL_SIZE

    def ghost_collides(self, nx, ny, maze):
        cx = nx + CELL_SIZE // 2
        cy = ny + CELL_SIZE // 2
        col = int(cx // CELL_SIZE)
        row = int(cy // CELL_SIZE)
        if 0 <= row < ROWS and 0 <= col < COLS:
            return maze[row][col] == 1
        return False

    def get_cell(self):
        return int((self.y + CELL_SIZE // 2) // CELL_SIZE), int((self.x + CELL_SIZE // 2) // CELL_SIZE)

    def frighten(self):
        if not self.eaten:
            self.frightened = True
            self.frighten_timer = 400


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PAC-MAN")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 20, bold=True)
        self.big_font = pygame.font.SysFont('Arial', 40, bold=True)
        self.reset()

    def reset(self):
        self.maze = [row[:] for row in MAZE]
        self.pacman = PacMan()
        self.ghosts = [Ghost(i) for i in range(4)]
        self.score = 0
        self.lives = 3
        self.state = 'playing'  # playing, dead, gameover, won
        self.dead_timer = 0
        self.total_dots = sum(row.count(2) + row.count(3) for row in MAZE)
        self.dots_eaten = 0
        self.ghost_combo = 0

    def draw_maze(self):
        for r in range(ROWS):
            for c in range(COLS):
                x = c * CELL_SIZE
                y = r * CELL_SIZE
                cell = self.maze[r][c]
                if cell == 1:
                    pygame.draw.rect(self.screen, BLUE, (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, DARK_BLUE, (x, y, CELL_SIZE, CELL_SIZE), 1)
                elif cell == 2:
                    pygame.draw.circle(self.screen, WHITE,
                        (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 2)
                elif cell == 3:
                    pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 2
                    pygame.draw.circle(self.screen, WHITE,
                        (x + CELL_SIZE // 2, y + CELL_SIZE // 2), int(5 + pulse))

    def draw_hud(self):
        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, SCREEN_HEIGHT - 35))
        for i in range(self.lives):
            lx = SCREEN_WIDTH - 30 - i * 25
            ly = SCREEN_HEIGHT - 28
            pygame.draw.circle(self.screen, YELLOW, (lx, ly), 8)
            pygame.draw.polygon(self.screen, BLACK, [(lx, ly), (lx + 8, ly - 4), (lx + 8, ly + 4)])

    def handle_dot_eating(self):
        pr, pc = self.pacman.get_cell()
        if 0 <= pr < ROWS and 0 <= pc < COLS:
            cell = self.maze[pr][pc]
            if cell == 2:
                self.maze[pr][pc] = 0
                self.score += 10
                self.dots_eaten += 1
            elif cell == 3:
                self.maze[pr][pc] = 0
                self.score += 50
                self.dots_eaten += 1
                self.ghost_combo = 0
                for g in self.ghosts:
                    g.frighten()

        if self.dots_eaten >= self.total_dots:
            self.state = 'won'

    def handle_ghost_collision(self):
        pr, pc = self.pacman.get_cell()
        for g in self.ghosts:
            gr, gc = g.get_cell()
            if abs(pr - gr) <= 1 and abs(pc - gc) <= 1:
                if g.frightened and not g.eaten:
                    g.eaten = True
                    g.frightened = False
                    self.ghost_combo += 1
                    pts = 200 * (2 ** (self.ghost_combo - 1))
                    self.score += pts
                elif not g.frightened and not g.eaten:
                    self.lives -= 1
                    self.state = 'dead'
                    self.dead_timer = 90
                    self.pacman.dying = True
                    return

    def run(self):
        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if self.state == 'playing':
                        if event.key in (pygame.K_LEFT, pygame.K_a):
                            self.pacman.next_dx, self.pacman.next_dy = -1, 0
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            self.pacman.next_dx, self.pacman.next_dy = 1, 0
                        elif event.key in (pygame.K_UP, pygame.K_w):
                            self.pacman.next_dx, self.pacman.next_dy = 0, -1
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self.pacman.next_dx, self.pacman.next_dy = 0, 1
                    if event.key == pygame.K_r:
                        self.reset()

            self.screen.fill(BLACK)
            self.draw_maze()

            if self.state == 'playing':
                self.pacman.update(self.maze)
                for g in self.ghosts:
                    g.update(self.maze, self.pacman)
                self.handle_dot_eating()
                self.handle_ghost_collision()

            elif self.state == 'dead':
                self.pacman.update(self.maze)
                self.dead_timer -= 1
                if self.dead_timer <= 0:
                    if self.lives <= 0:
                        self.state = 'gameover'
                    else:
                        self.pacman.reset()
                        for g in self.ghosts:
                            g.reset()
                        self.state = 'playing'

            self.pacman.draw(self.screen)
            for g in self.ghosts:
                g.draw(self.screen)

            self.draw_hud()

            if self.state == 'gameover':
                txt = self.big_font.render("GAME OVER", True, RED)
                self.screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
                rtxt = self.font.render("Press R to restart", True, WHITE)
                self.screen.blit(rtxt, (SCREEN_WIDTH // 2 - rtxt.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

            elif self.state == 'won':
                txt = self.big_font.render("YOU WIN!", True, YELLOW)
                self.screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
                rtxt = self.font.render("Press R to play again", True, WHITE)
                self.screen.blit(rtxt, (SCREEN_WIDTH // 2 - rtxt.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

            pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()