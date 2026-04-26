import pygame
import sys
import random

# Initialize
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Random Maze Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 0)
WALL_COLOR = (100, 100, 255)
GOAL_COLOR = (255, 215, 0)

# Maze dimensions (odd numbers for proper walls)
ROWS = 21
COLS = 21

class Maze:
    def __init__(self):
        self.grid = [[1 for _ in range(COLS)] for _ in range(ROWS)]
        self.start = (1, 1)
        self.end = (ROWS-2, COLS-2)
        self.generate()
    
    def generate(self):
        # Recursive backtracking to carve paths
        stack = []
        # start at (1,1)
        self.grid[1][1] = 0
        stack.append((1,1))
        
        while stack:
            x, y = stack[-1]
            neighbors = []
            # check 2 steps away in cardinal directions
            for dx, dy in [(2,0), (-2,0), (0,2), (0,-2)]:
                nx, ny = x+dx, y+dy
                if 0 < nx < ROWS-1 and 0 < ny < COLS-1 and self.grid[nx][ny] == 1:
                    neighbors.append((nx, ny, dx//2, dy//2))
            if neighbors:
                nx, ny, cx, cy = random.choice(neighbors)
                # carve path to neighbor
                self.grid[nx][ny] = 0
                self.grid[x + cx][y + cy] = 0
                stack.append((nx, ny))
            else:
                stack.pop()
        
        # Ensure start and end are paths
        self.grid[self.start[0]][self.start[1]] = 0
        self.grid[self.end[0]][self.end[1]] = 0
        # Add a few extra open spaces for variety
        for _ in range(20):
            rx = random.randint(2, ROWS-3)
            ry = random.randint(2, COLS-3)
            self.grid[rx][ry] = 0
    
    def draw(self, surf):
        cell_w = min(WIDTH // COLS, HEIGHT // ROWS)
        offset_x = (WIDTH - COLS * cell_w) // 2
        offset_y = (HEIGHT - ROWS * cell_w) // 2
        for r in range(ROWS):
            for c in range(COLS):
                x = offset_x + c * cell_w
                y = offset_y + r * cell_w
                if self.grid[r][c] == 1:
                    pygame.draw.rect(surf, WALL_COLOR, (x, y, cell_w, cell_w))
                    pygame.draw.rect(surf, BLACK, (x, y, cell_w, cell_w), 1)
        # draw goal
        gx = offset_x + self.end[1] * cell_w
        gy = offset_y + self.end[0] * cell_w
        pygame.draw.rect(surf, GOAL_COLOR, (gx, gy, cell_w, cell_w))
        pygame.draw.circle(surf, YELLOW, (gx + cell_w//2, gy + cell_w//2), cell_w//3)
        return offset_x, offset_y, cell_w

class Player:
    def __init__(self, maze):
        self.maze = maze
        self.row, self.col = maze.start
        self.cell_w = 0
        self.offset_x = 0
        self.offset_y = 0
        self.color = GREEN
    
    def update_drawing_params(self, off_x, off_y, c_w):
        self.offset_x = off_x
        self.offset_y = off_y
        self.cell_w = c_w
    
    def move(self, dr, dc):
        nr = self.row + dr
        nc = self.col + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and self.maze.grid[nr][nc] == 0:
            self.row = nr
            self.col = nc
            return True
        return False
    
    def draw(self, surf):
        center_x = self.offset_x + self.col * self.cell_w + self.cell_w//2
        center_y = self.offset_y + self.row * self.cell_w + self.cell_w//2
        pygame.draw.circle(surf, self.color, (center_x, center_y), self.cell_w//3)
    
    def reset(self, maze):
        self.maze = maze
        self.row, self.col = maze.start

def show_message(surf, text, color, y_offset=0):
    text_surf = big_font.render(text, True, color)
    rect = text_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + y_offset))
    surf.blit(text_surf, rect)

def game():
    maze = Maze()
    player = Player(maze)
    win = False
    running = True
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if win:
                    if event.key == pygame.K_r:
                        # generate new random maze
                        maze = Maze()
                        player.reset(maze)
                        win = False
                    elif event.key == pygame.K_q:
                        running = False
                else:
                    if event.key == pygame.K_UP:
                        player.move(-1, 0)
                    elif event.key == pygame.K_DOWN:
                        player.move(1, 0)
                    elif event.key == pygame.K_LEFT:
                        player.move(0, -1)
                    elif event.key == pygame.K_RIGHT:
                        player.move(0, 1)
        
        # check win condition
        if (player.row, player.col) == maze.end and not win:
            win = True
        
        # draw
        screen.fill(BLACK)
        off_x, off_y, c_w = maze.draw(screen)
        player.update_drawing_params(off_x, off_y, c_w)
        player.draw(screen)
        
        if win:
            show_message(screen, "YOU WIN! New maze?", GREEN, -30)
            show_message(screen, "Press R for new random maze, Q to quit", WHITE, 30)
        else:
            instr = font.render("Arrow keys to move → find the gold square → win → new maze", True, WHITE)
            screen.blit(instr, (10, HEIGHT - 30))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game()