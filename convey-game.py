import pygame
import sys
import random

WIDTH, HEIGHT = 900, 700
CELL = 12
COLS = WIDTH // CELL
ROWS = HEIGHT // CELL
FPS = 15

BG = (10, 10, 20)
CELL_CLR = (0, 220, 120)
GRID_CLR = (25, 25, 40)
UI_CLR = (180, 180, 200)
PAUSE_CLR = (220, 80, 80)

def empty():
    return [[0]*COLS for _ in range(ROWS)]

def random_board():
    return [[random.choice([0,0,0,1]) for _ in range(COLS)] for _ in range(ROWS)]

def next_gen(board):
    new = empty()
    for r in range(ROWS):
        for c in range(COLS):
            neighbors = sum(
                board[(r+dr) % ROWS][(c+dc) % COLS]
                for dr in (-1,0,1) for dc in (-1,0,1)
                if (dr,dc) != (0,0)
            )
            if board[r][c]:
                new[r][c] = 1 if neighbors in (2,3) else 0
            else:
                new[r][c] = 1 if neighbors == 3 else 0
    return new

def draw(screen, board, font, paused, gen):
    screen.fill(BG)
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(c*CELL, r*CELL, CELL-1, CELL-1)
            if board[r][c]:
                pygame.draw.rect(screen, CELL_CLR, rect, border_radius=2)
            else:
                pygame.draw.rect(screen, GRID_CLR, rect)

    status = f"  GEN: {gen}   |   SPACE=pause   R=random   C=clear   Click=draw"
    if paused:
        status = f"  ⏸ PAUSED   GEN: {gen}   |   SPACE=resume   R=random   C=clear   Click=draw"
    lbl = font.render(status, True, PAUSE_CLR if paused else UI_CLR)
    pygame.draw.rect(screen, (10,10,20), (0, HEIGHT-26, WIDTH, 26))
    screen.blit(lbl, (4, HEIGHT-22))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Conway's Game of Life")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 16)

    board = random_board()
    paused = False
    gen = 0
    drawing = False
    erase = False

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    paused = not paused
                if e.key == pygame.K_r:
                    board = random_board(); gen = 0
                if e.key == pygame.K_c:
                    board = empty(); gen = 0
            if e.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                mx, my = e.pos
                r, c = my // CELL, mx // CELL
                if 0 <= r < ROWS and 0 <= c < COLS:
                    erase = board[r][c] == 1
            if e.type == pygame.MOUSEBUTTONUP:
                drawing = False
            if e.type == pygame.MOUSEMOTION and drawing:
                mx, my = e.pos
                r, c = my // CELL, mx // CELL
                if 0 <= r < ROWS and 0 <= c < COLS:
                    board[r][c] = 0 if erase else 1

        if not paused:
            board = next_gen(board)
            gen += 1

        draw(screen, board, font, paused, gen)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()