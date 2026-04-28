import pygame
import random
import sys

SIZE = 4
TILE = 120
GAP = 6
PAD = 60
WIN_W = SIZE * (TILE + GAP) + GAP + PAD * 2
WIN_H = WIN_W + 80
FPS = 60

BG = (30, 30, 40)
TILE_CLR = (70, 130, 180)
TILE_HOVER = (100, 160, 210)
EMPTY_CLR = (20, 20, 30)
TEXT_CLR = (255, 255, 255)
WIN_CLR = (80, 200, 120)

def new_board():
    nums = list(range(1, SIZE * SIZE)) + [0]
    while True:
        random.shuffle(nums)
        if is_solvable(nums):
            return nums

def is_solvable(board):
    inv = 0
    flat = [x for x in board if x != 0]
    for i in range(len(flat)):
        for j in range(i + 1, len(flat)):
            if flat[i] > flat[j]:
                inv += 1
    blank_row = board.index(0) // SIZE
    if SIZE % 2 == 1:
        return inv % 2 == 0
    else:
        return (inv + blank_row) % 2 == 1

def is_solved(board):
    return board == list(range(1, SIZE * SIZE)) + [0]

def get_moves(board):
    z = board.index(0)
    r, c = divmod(z, SIZE)
    moves = []
    if r > 0: moves.append(z - SIZE)
    if r < SIZE - 1: moves.append(z + SIZE)
    if c > 0: moves.append(z - 1)
    if c < SIZE - 1: moves.append(z + 1)
    return moves

def slide(board, idx):
    z = board.index(0)
    b = board[:]
    b[z], b[idx] = b[idx], b[z]
    return b

def tile_rect(idx):
    r, c = divmod(idx, SIZE)
    x = PAD + c * (TILE + GAP) + GAP
    y = PAD + r * (TILE + GAP) + GAP
    return pygame.Rect(x, y, TILE, TILE)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Sliding Puzzle")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 42, bold=True)
    small = pygame.font.SysFont("consolas", 22)

    board = new_board()
    moves = 0
    won = False

    while True:
        mx, my = pygame.mouse.get_pos()
        valid_moves = get_moves(board)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                board = new_board(); moves = 0; won = False
            if e.type == pygame.MOUSEBUTTONDOWN and not won:
                for idx in valid_moves:
                    if tile_rect(idx).collidepoint(mx, my):
                        board = slide(board, idx)
                        moves += 1
                        if is_solved(board):
                            won = True

        screen.fill(BG)

        for idx, val in enumerate(board):
            rect = tile_rect(idx)
            if val == 0:
                pygame.draw.rect(screen, EMPTY_CLR, rect, border_radius=12)
            else:
                hover = idx in valid_moves and rect.collidepoint(mx, my) and not won
                color = WIN_CLR if won else (TILE_HOVER if hover else TILE_CLR)
                pygame.draw.rect(screen, color, rect, border_radius=12)
                txt = font.render(str(val), True, TEXT_CLR)
                screen.blit(txt, txt.get_rect(center=rect.center))

        msg = "YOU WIN! 🎉  R=restart" if won else f"Moves: {moves}    R=restart"
        label = small.render(msg, True, WIN_CLR if won else TEXT_CLR)
        screen.blit(label, label.get_rect(center=(WIN_W // 2, WIN_H - 35)))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()