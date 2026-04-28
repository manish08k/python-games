
import pygame
import sys

pygame.init()

CELL = 52
PAD = 30
CLUE_W = 320
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_BLUE = (180, 215, 255)
BLUE = (55, 138, 221)
GREEN_BG = (220, 245, 220)
GREEN = (50, 160, 80)
GRAY = (180, 180, 180)
DARK = (30, 30, 40)
BG = (245, 244, 240)
RED = (220, 60, 60)

WORDS = [
    {'id':'1A','num':1,'dir':'A','row':0,'col':1,'word':'CRANE', 'clue':'Large wading bird'},
    {'id':'2A','num':2,'dir':'A','row':2,'col':1,'word':'TIGER', 'clue':'Striped big cat'},
    {'id':'3A','num':3,'dir':'A','row':4,'col':1,'word':'PLANET','clue':'Orbits a star'},
    {'id':'4A','num':4,'dir':'A','row':5,'col':6,'word':'ORBIT', 'clue':'Path around a celestial body'},
    {'id':'5A','num':5,'dir':'A','row':7,'col':0,'word':'MOON',  'clue':"Earth's natural satellite"},
    {'id':'6A','num':6,'dir':'A','row':9,'col':5,'word':'EARTH', 'clue':'Our home planet'},
    {'id':'1D','num':1,'dir':'D','row':0,'col':1,'word':'CAT',   'clue':'Feline companion'},
    {'id':'7D','num':7,'dir':'D','row':0,'col':3,'word':'EAGLE', 'clue':'Large bird of prey'},
    {'id':'8D','num':8,'dir':'D','row':0,'col':5,'word':'EATEN', 'clue':'Consumed food'},
    {'id':'2D','num':2,'dir':'D','row':2,'col':1,'word':'TAPE',  'clue':'Sticky strip'},
    {'id':'3D','num':3,'dir':'D','row':4,'col':1,'word':'PONE',  'clue':'Type of cornbread'},
    {'id':'9D','num':9,'dir':'D','row':4,'col':3,'word':'NORI',  'clue':'Seaweed for sushi'},
    {'id':'4D','num':4,'dir':'D','row':5,'col':6,'word':'ORIT',  'clue':'Orbiting route'},
]

GRID_H, GRID_W = 11, 11

def build_grid():
    grid = [['#']*GRID_W for _ in range(GRID_H)]
    for w in WORDS:
        r, c = w['row'], w['col']
        for i, ch in enumerate(w['word']):
            if w['dir'] == 'A':
                if c+i < GRID_W: grid[r][c+i] = ch
            else:
                if r+i < GRID_H: grid[r+i][c] = ch
    return grid

def build_numbers(solution):
    nums = {}
    counter = 1
    used = set()
    word_starts = set((w['row'], w['col']) for w in WORDS)
    for r in range(GRID_H):
        for c in range(GRID_W):
            if solution[r][c] != '#' and (r,c) in word_starts:
                if (r,c) not in used:
                    nums[(r,c)] = counter
                    counter += 1
                    used.add((r,c))
    # Assign proper numbers from WORDS
    nums2 = {}
    assigned = {}
    n = 1
    for r in range(GRID_H):
        for c in range(GRID_W):
            if solution[r][c] == '#': continue
            starts_across = (c == 0 or solution[r][c-1] == '#') and c+1 < GRID_W and solution[r][c+1] != '#'
            starts_down   = (r == 0 or solution[r-1][c] == '#') and r+1 < GRID_H and solution[r+1][c] != '#'
            if starts_across or starts_down:
                nums2[(r,c)] = n
                assigned[(r,c)] = n
                n += 1
    return nums2

solution = build_grid()
numbers  = build_numbers(solution)

user_grid = [['' if solution[r][c] != '#' else '#' for c in range(GRID_W)] for r in range(GRID_H)]
checked   = [[False]*GRID_W for _ in range(GRID_H)]
revealed  = [[False]*GRID_W for _ in range(GRID_H)]

TOTAL_W = PAD + GRID_W*CELL + PAD + CLUE_W + PAD
TOTAL_H = PAD + GRID_H*CELL + PAD + 60

screen = pygame.display.set_mode((TOTAL_W, TOTAL_H))
pygame.display.set_caption("Crossword Puzzle")
clock  = pygame.time.Clock()

font_cell   = pygame.font.SysFont("consolas", 22, bold=True)
font_num    = pygame.font.SysFont("consolas", 11)
font_clue   = pygame.font.SysFont("consolas", 13)
font_head   = pygame.font.SysFont("consolas", 14, bold=True)
font_status = pygame.font.SysFont("consolas", 15, bold=True)

selected_cell = None
selected_dir  = 'A'
selected_word = None

def word_cells(w):
    cells = []
    for i in range(len(w['word'])):
        if w['dir'] == 'A': cells.append((w['row'], w['col']+i))
        else:                cells.append((w['row']+i, w['col']))
    return cells

def find_word(r, c, direction):
    for w in WORDS:
        if w['dir'] == direction:
            cells = word_cells(w)
            if (r,c) in cells:
                return w
    return None

def select_cell(r, c):
    global selected_cell, selected_dir, selected_word
    if solution[r][c] == '#': return
    if selected_cell == (r,c):
        selected_dir = 'D' if selected_dir == 'A' else 'A'
    selected_cell = (r,c)
    w = find_word(r, c, selected_dir)
    if not w:
        selected_dir = 'D' if selected_dir == 'A' else 'A'
        w = find_word(r, c, selected_dir)
    selected_word = w

def next_cell():
    global selected_cell
    if not selected_word or not selected_cell: return
    cells = word_cells(selected_word)
    idx = cells.index(selected_cell) if selected_cell in cells else -1
    if idx < len(cells)-1:
        nr, nc = cells[idx+1]
        selected_cell = (nr, nc)
def prev_cell():
    global selected_cell
    if not selected_word or not selected_cell: return
    cells = word_cells(selected_word)
    idx = cells.index(selected_cell) if selected_cell in cells else -1
    if idx > 0:
        nr, nc = cells[idx-1]
        selected_cell = (nr, nc)

def check_all():
    for w in WORDS:
        for i,(r,c) in enumerate(word_cells(w)):
            if user_grid[r][c] != '':
                checked[r][c] = True

def reveal_all():
    for r in range(GRID_H):
        for c in range(GRID_W):
            if solution[r][c] != '#':
                user_grid[r][c] = solution[r][c]
                revealed[r][c]  = True

def clear_all():
    for r in range(GRID_H):
        for c in range(GRID_W):
            if solution[r][c] != '#' and not revealed[r][c]:
                user_grid[r][c] = ''
                checked[r][c]   = False

def is_solved():
    for r in range(GRID_H):
        for c in range(GRID_W):
            if solution[r][c] != '#' and user_grid[r][c] != solution[r][c]:
                return False
    return True

def draw():
    screen.fill(BG)
    gx = PAD
    gy = PAD

    highlight_cells = set(word_cells(selected_word)) if selected_word else set()

    for r in range(GRID_H):
        for c in range(GRID_W):
            x = gx + c*CELL
            y = gy + r*CELL
            rect = pygame.Rect(x, y, CELL-1, CELL-1)

            if solution[r][c] == '#':
                pygame.draw.rect(screen, BLACK, rect)
                continue

            # Cell background
            if (r,c) == selected_cell:
                pygame.draw.rect(screen, LIGHT_BLUE, rect)
            elif (r,c) in highlight_cells:
                pygame.draw.rect(screen, (220, 235, 255), rect)
            elif revealed[r][c]:
                pygame.draw.rect(screen, GREEN_BG, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect)

            pygame.draw.rect(screen, GRAY, rect, 1)

            # Number
            if (r,c) in numbers:
                ns = font_num.render(str(numbers[(r,c)]), True, DARK)
                screen.blit(ns, (x+2, y+2))

            # Letter
            letter = user_grid[r][c]
            if letter:
                correct = letter == solution[r][c]
                if revealed[r][c]:
                    col = GREEN
                elif checked[r][c]:
                    col = GREEN if correct else RED
                else:
                    col = DARK
                ls = font_cell.render(letter, True, col)
                screen.blit(ls, ls.get_rect(center=(x+CELL//2, y+CELL//2)))

    # Grid border
    pygame.draw.rect(screen, DARK, (gx, gy, GRID_W*CELL, GRID_H*CELL), 2)

    # Clues panel
    cx = gx + GRID_W*CELL + PAD
    cy = gy

    across = [w for w in WORDS if w['dir']=='A']
    down   = [w for w in WORDS if w['dir']=='D']

    panel_h = GRID_H*CELL
    pygame.draw.rect(screen, WHITE, (cx, cy, CLUE_W-10, panel_h), border_radius=8)
    pygame.draw.rect(screen, GRAY,  (cx, cy, CLUE_W-10, panel_h), 1, border_radius=8)

    yy = cy + 10
    ah = font_head.render("ACROSS", True, BLUE)
    screen.blit(ah, (cx+10, yy)); yy += 22

    for w in across:
        active = (selected_word and selected_word['id'] == w['id'])
        col    = BLUE if active else DARK
        txt    = f"{w['num']}. {w['clue']}"
        if len(txt) > 32: txt = txt[:31]+'…'
        ts = font_clue.render(txt, True, col)
        if active:
            pygame.draw.rect(screen, (230,240,255), (cx+6, yy-1, CLUE_W-22, 16), border_radius=3)
        screen.blit(ts, (cx+10, yy)); yy += 18

    yy += 8
    dh = font_head.render("DOWN", True, BLUE)
    screen.blit(dh, (cx+10, yy)); yy += 22

    for w in down:
        active = (selected_word and selected_word['id'] == w['id'])
        col    = BLUE if active else DARK
        txt    = f"{w['num']}. {w['clue']}"
        if len(txt) > 32: txt = txt[:31]+'…'
        ts = font_clue.render(txt, True, col)
        if active:
            pygame.draw.rect(screen, (230,240,255), (cx+6, yy-1, CLUE_W-22, 16), border_radius=3)
        screen.blit(ts, (cx+10, yy)); yy += 18

    # Toolbar
    by = gy + GRID_H*CELL + 12
    buttons = [("CHECK", TOTAL_W//2-160, check_all),
               ("REVEAL", TOTAL_W//2-60, reveal_all),
               ("CLEAR",  TOTAL_W//2+40, clear_all)]
    for label, bx, _ in buttons:
        br = pygame.Rect(bx, by, 90, 32)
        pygame.draw.rect(screen, WHITE, br, border_radius=6)
        pygame.draw.rect(screen, GRAY,  br, 1, border_radius=6)
        ls = font_status.render(label, True, DARK)
        screen.blit(ls, ls.get_rect(center=br.center))

    if is_solved():
        ws = font_status.render("✓  Puzzle Complete!", True, GREEN)
        screen.blit(ws, (PAD, by+8))

    pygame.display.flip()
    return buttons, by

running = True
buttons_cache = []
by_cache = 0

while running:
    buttons_cache, by_cache = draw()
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.MOUSEBUTTONDOWN:
            mx, my = e.pos
            # Toolbar
            for label, bx, action in buttons_cache:
                if pygame.Rect(bx, by_cache, 90, 32).collidepoint(mx, my):
                    action()
            # Grid
            gx, gy = PAD, PAD
            gc = (mx - gx) // CELL
            gr = (my - gy) // CELL
            if 0 <= gr < GRID_H and 0 <= gc < GRID_W:
                select_cell(gr, gc)
            # Clue click
            cx = gx + GRID_W*CELL + PAD
            if mx >= cx:
                pass  # clue click optional

        if e.type == pygame.KEYDOWN and selected_cell:
            r, c = selected_cell
            if e.key == pygame.K_BACKSPACE:
                if user_grid[r][c] and not revealed[r][c]:
                    user_grid[r][c] = ''
                    checked[r][c] = False
                else:
                    prev_cell()
            elif e.key == pygame.K_TAB:
                selected_dir = 'D' if selected_dir == 'A' else 'A'
                selected_word = find_word(r, c, selected_dir)
            elif e.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                dr = {pygame.K_UP:-1,pygame.K_DOWN:1}.get(e.key,0)
                dc = {pygame.K_LEFT:-1,pygame.K_RIGHT:1}.get(e.key,0)
                nr,nc = r+dr, c+dc
                if 0<=nr<GRID_H and 0<=nc<GRID_W and solution[nr][nc]!='#':
                    selected_cell=(nr,nc)
                    selected_word=find_word(nr,nc,selected_dir)
            elif e.unicode.isalpha():
                if not revealed[r][c]:
                    user_grid[r][c] = e.unicode.upper()
                    checked[r][c] = False
                    next_cell()

    clock.tick(FPS)

pygame.quit()
sys.exit()