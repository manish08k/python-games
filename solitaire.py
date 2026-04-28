import pygame
import random
import sys

pygame.init()

# --- Constants ---
W, H = 900, 700
CARD_W, CARD_H = 80, 110
GAP = 20
FPS = 60

GREEN_FELT  = (25, 100, 60)
GREEN_DARK  = (18, 75, 45)
WHITE       = (255, 255, 255)
BLACK       = (10, 10, 10)
RED         = (192, 40, 40)
GOLD        = (212, 175, 55)
GRAY        = (160, 160, 160)
SLOT_COLOR  = (18, 80, 48)
SLOT_BORDER = (30, 120, 70)
SHADOW      = (10, 60, 35)

SUITS  = ['♠', '♥', '♦', '♣']
RANKS  = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
RED_S  = {'♥', '♦'}

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("♠ Klondike Solitaire ♣")
clock  = pygame.time.Clock()

font_lg  = pygame.font.SysFont("Georgia", 22, bold=True)
font_md  = pygame.font.SysFont("Georgia", 15, bold=True)
font_sm  = pygame.font.SysFont("Georgia", 12)
font_win = pygame.font.SysFont("Georgia", 52, bold=True)

# --- Card class ---
class Card:
    def __init__(self, suit, rank):
        self.suit  = suit
        self.rank  = rank
        self.face_up = False
        self.x = self.y = 0

    @property
    def value(self):
        return RANKS.index(self.rank) + 1

    @property
    def color(self):
        return 'red' if self.suit in RED_S else 'black'

    def draw(self, surface, x, y, selected=False):
        self.x, self.y = x, y
        shadow_r = pygame.Rect(x+3, y+3, CARD_W, CARD_H)
        pygame.draw.rect(surface, SHADOW, shadow_r, border_radius=7)

        r = pygame.Rect(x, y, CARD_W, CARD_H)
        if not self.face_up:
            pygame.draw.rect(surface, (30, 60, 140), r, border_radius=7)
            pygame.draw.rect(surface, (50, 80, 180), r, 2, border_radius=7)
            # card back pattern
            inner = pygame.Rect(x+5, y+5, CARD_W-10, CARD_H-10)
            pygame.draw.rect(surface, (20, 45, 110), inner, border_radius=4)
            for i in range(4, CARD_W-8, 8):
                pygame.draw.line(surface, (35, 65, 150), (x+i, y+5), (x+5, y+i), 1)
        else:
            bg = (255, 252, 245) if not selected else (255, 245, 180)
            pygame.draw.rect(surface, bg, r, border_radius=7)
            pygame.draw.rect(surface, GOLD if selected else (180, 170, 130), r, 2, border_radius=7)
            col = RED if self.color == 'red' else BLACK
            # top-left
            t1 = font_md.render(self.rank, True, col)
            t2 = font_sm.render(self.suit, True, col)
            surface.blit(t1, (x+5, y+3))
            surface.blit(t2, (x+5, y+22))
            # bottom-right (rotated)
            t3 = font_md.render(self.rank, True, col)
            t4 = font_sm.render(self.suit, True, col)
            surface.blit(pygame.transform.rotate(t3, 180), (x+CARD_W-t3.get_width()-5, y+CARD_H-t3.get_height()-20))
            surface.blit(pygame.transform.rotate(t4, 180), (x+CARD_W-t4.get_width()-5, y+CARD_H-t4.get_height()-5))
            # center suit
            cs = pygame.font.SysFont("Georgia", 30).render(self.suit, True, col)
            surface.blit(cs, (x + CARD_W//2 - cs.get_width()//2, y + CARD_H//2 - cs.get_height()//2))

    def rect(self):
        return pygame.Rect(self.x, self.y, CARD_W, CARD_H)


# --- Game state ---
def new_game():
    deck = [Card(s, r) for s in SUITS for r in RANKS]
    random.shuffle(deck)
    tableau = [[] for _ in range(7)]
    for i in range(7):
        for j in range(i+1):
            c = deck.pop()
            c.face_up = (j == i)
            tableau[i].append(c)
    stock   = deck
    waste   = []
    found   = [[] for _ in range(4)]
    return tableau, stock, waste, found

tableau, stock, waste, foundations = new_game()
selected     = None   # (source, cards, orig_pos)
score        = 0
moves        = 0
won          = False

# Layout helpers
def tab_x(col):  return GAP + col * (CARD_W + GAP)
def tab_y(col, row, pile):
    base = 160
    step = 20 if not pile[row].face_up else 28
    return base + row * step

def stock_x():   return GAP
def stock_y():   return GAP
def waste_x():   return GAP + CARD_W + GAP
def waste_y():   return GAP
def found_x(i):  return GAP + (3 + i) * (CARD_W + GAP)
def found_y():   return GAP


def draw_slot(surface, x, y, label=""):
    r = pygame.Rect(x, y, CARD_W, CARD_H)
    pygame.draw.rect(surface, SLOT_COLOR, r, border_radius=7)
    pygame.draw.rect(surface, SLOT_BORDER, r, 2, border_radius=7)
    if label:
        t = font_lg.render(label, True, SLOT_BORDER)
        surface.blit(t, (x + CARD_W//2 - t.get_width()//2, y + CARD_H//2 - t.get_height()//2))


def draw_board():
    global won
    screen.fill(GREEN_FELT)
    # subtle noise texture via lines
    for yy in range(0, H, 4):
        pygame.draw.line(screen, GREEN_DARK, (0, yy), (W, yy), 1)

    # --- Top bar ---
    pygame.draw.rect(screen, (15, 60, 35), (0, 0, W, 140))

    # Stock
    draw_slot(screen, stock_x(), stock_y(), "")
    if stock:
        stock[-1].face_up = False
        stock[-1].draw(screen, stock_x(), stock_y())
    else:
        t = font_lg.render("↺", True, SLOT_BORDER)
        screen.blit(t, (stock_x() + CARD_W//2 - t.get_width()//2, stock_y() + CARD_H//2 - t.get_height()//2))

    # Waste
    draw_slot(screen, waste_x(), waste_y(), "")
    if waste:
        waste[-1].face_up = True
        waste[-1].draw(screen, waste_x(), waste_y())

    # Foundations
    suit_labels = ['♠', '♥', '♦', '♣']
    for i in range(4):
        draw_slot(screen, found_x(i), found_y(), suit_labels[i])
        if foundations[i]:
            foundations[i][-1].face_up = True
            foundations[i][-1].draw(screen, found_x(i), found_y())

    # Score / moves
    sc = font_md.render(f"Score: {score}   Moves: {moves}", True, (200, 220, 180))
    screen.blit(sc, (W//2 - sc.get_width()//2, 10))
    hint = font_sm.render("Click stock to draw  •  Double-click to auto-move  •  N = new game", True, (120, 160, 110))
    screen.blit(hint, (W//2 - hint.get_width()//2, 120))

    # Tableau
    sel_cards = selected[1] if selected else []
    for col, pile in enumerate(tableau):
        cx = tab_x(col)
        draw_slot(screen, cx, 160, "")
        for row, card in enumerate(pile):
            cy = tab_y(col, row, pile)
            card.draw(screen, cx, cy, selected=(card in sel_cards))

    # Dragging ghost
    if selected:
        mx, my = pygame.mouse.get_pos()
        ox, oy = selected[2]
        for i, card in enumerate(selected[1]):
            card.draw(screen, mx - ox, my - oy + i * 28)

    # Win screen
    if won:
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        t1 = font_win.render("YOU WIN! 🎉", True, GOLD)
        t2 = font_md.render(f"Score: {score}   Moves: {moves}", True, WHITE)
        t3 = font_md.render("Press N for a new game", True, (180, 220, 180))
        screen.blit(t1, (W//2 - t1.get_width()//2, H//2 - 80))
        screen.blit(t2, (W//2 - t2.get_width()//2, H//2 + 20))
        screen.blit(t3, (W//2 - t3.get_width()//2, H//2 + 60))

    pygame.display.flip()


def can_place_on_tableau(card, pile):
    if not pile:
        return card.rank == 'K'
    top = pile[-1]
    if not top.face_up:
        return False
    return top.value == card.value + 1 and top.color != card.color


def can_place_on_foundation(card, pile):
    if not pile:
        return card.rank == 'A'
    top = pile[-1]
    return top.suit == card.suit and top.value == card.value - 1


def auto_to_foundation(card, source_pile):
    global score, moves
    for i, fp in enumerate(foundations):
        if can_place_on_foundation(card, fp):
            source_pile.remove(card)
            fp.append(card)
            card.face_up = True
            score += 15
            moves += 1
            if source_pile and not source_pile[-1].face_up:
                source_pile[-1].face_up = True
                score += 5
            return True
    return False


def check_win():
    return all(len(fp) == 13 for fp in foundations)


def get_card_at(mx, my):
    # Check waste top
    if waste:
        c = waste[-1]
        if c.rect().collidepoint(mx, my):
            return ('waste', [c], waste)
    # Check foundations
    for i, fp in enumerate(foundations):
        if fp:
            c = fp[-1]
            if c.rect().collidepoint(mx, my):
                return ('found', [c], fp)
    # Check tableau (top-down, last card first for stacks)
    for col, pile in enumerate(tableau):
        for row in range(len(pile)-1, -1, -1):
            card = pile[row]
            if not card.face_up:
                continue
            cr = pygame.Rect(card.x, card.y, CARD_W,
                             28 if row < len(pile)-1 else CARD_H)
            if cr.collidepoint(mx, my):
                cards = pile[row:]
                return ('tab', cards, pile)
    return None


last_click_time = 0
last_click_card = None

running = True
while running:
    clock.tick(FPS)
    draw_board()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                tableau, stock, waste, foundations = new_game()
                selected = None
                score = moves = 0
                won = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not won:
            mx, my = event.pos
            now = pygame.time.get_ticks()

            # Click stock
            sr = pygame.Rect(stock_x(), stock_y(), CARD_W, CARD_H)
            if sr.collidepoint(mx, my):
                if stock:
                    c = stock.pop()
                    c.face_up = True
                    waste.append(c)
                    moves += 1
                else:
                    # Reset stock from waste
                    stock = list(reversed(waste))
                    for c in stock: c.face_up = False
                    waste = []
                    score = max(0, score - 100)
                    moves += 1
                selected = None
                continue

            hit = get_card_at(mx, my)
            if hit:
                src, cards, pile = hit
                # Double-click auto move
                if now - last_click_time < 350 and last_click_card is cards[0]:
                    auto_to_foundation(cards[0], pile)
                    selected = None
                    if check_win(): won = True
                else:
                    last_click_time = now
                    last_click_card = cards[0]
                    # Start drag
                    ox = mx - cards[0].x
                    oy = my - cards[0].y
                    selected = (src, cards, (ox, oy))
            else:
                selected = None

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and selected:
            mx, my = event.pos
            src, cards, orig = selected
            card = cards[0]
            dropped = False

            # Try foundation drop (single card only)
            if len(cards) == 1:
                for i, fp in enumerate(foundations):
                    fr = pygame.Rect(found_x(i), found_y(), CARD_W, CARD_H)
                    if fr.collidepoint(mx, my) and can_place_on_foundation(card, fp):
                        # Remove from source
                        if src == 'waste':   waste.remove(card)
                        elif src == 'tab':   tableau[tableau.index(cards[0].__class__) if False else [p for p in tableau if card in p][0].index(card):]
                        # simpler:
                        for pile in tableau:
                            if card in pile:
                                pile.remove(card)
                                if pile and not pile[-1].face_up:
                                    pile[-1].face_up = True
                                    score += 5
                                break
                        if src == 'waste' and card in waste: waste.remove(card)
                        fp.append(card)
                        card.face_up = True
                        score += 15
                        moves += 1
                        dropped = True
                        if check_win(): won = True
                        break

            # Try tableau drop
            if not dropped:
                for col, pile in enumerate(tableau):
                    cr = pygame.Rect(tab_x(col), 160, CARD_W,
                                     tab_y(col, len(pile)-1, pile) + CARD_H - 160 if pile else CARD_H)
                    target_r = pygame.Rect(tab_x(col), 160 if not pile else pile[-1].y,
                                           CARD_W, CARD_H + 50)
                    if target_r.collidepoint(mx, my) and can_place_on_tableau(card, pile):
                        # Remove from source pile
                        for c in cards:
                            for p in tableau:
                                if c in p: p.remove(c)
                            if c in waste: waste.remove(c)
                        for c in cards:
                            pile.append(c)
                        # Flip newly exposed card
                        for p in tableau:
                            if p and not p[-1].face_up:
                                p[-1].face_up = True
                                score += 5
                        score += 5
                        moves += 1
                        dropped = True
                        break

            selected = None

    if won and not any(event.type == pygame.KEYDOWN for event in pygame.event.get()):
        pass

pygame.quit()
sys.exit()
