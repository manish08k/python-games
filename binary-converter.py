import pygame
import sys
import random
import time

pygame.init()

W, H = 900, 620
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Binary Converter Game")
clock = pygame.time.Clock()

# Colors
BG       = (8, 12, 24)
PANEL    = (16, 22, 40)
BORDER   = (40, 55, 90)
WHITE    = (220, 228, 245)
GRAY     = (100, 115, 145)
YELLOW   = (255, 210, 50)
GREEN    = (60, 210, 110)
RED      = (220, 65, 65)
BLUE     = (60, 145, 255)
CYAN     = (50, 210, 225)
PURPLE   = (175, 95, 255)
ORANGE   = (255, 155, 50)
DARK_G   = (20, 35, 20)
DARK_R   = (35, 12, 12)
BIT_ON   = (60, 210, 110)
BIT_OFF  = (25, 35, 55)
BIT_BDR  = (50, 180, 95)
BIT_BDR2 = (40, 55, 90)

F_HUGE  = pygame.font.SysFont("consolas", 52, bold=True)
F_BIG   = pygame.font.SysFont("consolas", 28, bold=True)
F_MED   = pygame.font.SysFont("consolas", 20, bold=True)
F_MAIN  = pygame.font.SysFont("consolas", 16)
F_SMALL = pygame.font.SysFont("consolas", 13)
F_MONO  = pygame.font.SysFont("consolas", 22, bold=True)

MODES = [
    {'id': 'dec_to_bin', 'label': 'Decimal → Binary',  'desc': 'Click bits to match the decimal number'},
    {'id': 'bin_to_dec', 'label': 'Binary → Decimal',  'desc': 'Type the decimal value of the binary number'},
    {'id': 'dec_to_hex', 'label': 'Decimal → Hex',     'desc': 'Type the hexadecimal value of the decimal'},
    {'id': 'hex_to_dec', 'label': 'Hex → Decimal',     'desc': 'Type the decimal value of the hex number'},
    {'id': 'bin_to_hex', 'label': 'Binary → Hex',      'desc': 'Type the hex value of the binary number'},
]

DIFFICULTIES = [
    {'label': 'Easy',   'bits': 4, 'max': 15,  'time': 30, 'points': 10},
    {'label': 'Medium', 'bits': 6, 'max': 63,  'time': 20, 'points': 20},
    {'label': 'Hard',   'bits': 8, 'max': 255, 'time': 15, 'points': 35},
]

STATE_MENU    = 'menu'
STATE_PLAY    = 'play'
STATE_RESULT  = 'result'
STATE_GAMEOVER= 'gameover'

# ── Game State ─────────────────────────────────────────────────────────────
state         = STATE_MENU
mode          = MODES[0]
difficulty    = DIFFICULTIES[0]
score         = 0
lives         = 3
streak        = 0
best_score    = 0
question_num  = 0
MAX_QUESTIONS = 10

target_num    = 0
bits          = [0] * 8
input_text    = ""
feedback      = ""
feedback_col  = WHITE
feedback_timer= 0
time_left     = 0
time_start    = 0
correct_ans   = ""
wrong_flash   = 0
correct_flash = 0
bit_rects     = []
hint_used     = False
particle_list = []

def new_question():
    global target_num, bits, input_text, feedback, time_left, time_start
    global correct_ans, hint_used, feedback_timer
    n_bits = difficulty['bits']
    target_num   = random.randint(1, difficulty['max'])
    bits         = [0] * 8
    input_text   = ""
    feedback      = ""
    feedback_timer= 0
    hint_used     = False
    time_left     = difficulty['time']
    time_start    = time.time()
    correct_ans   = compute_answer()

def compute_answer():
    m = mode['id']
    if m == 'dec_to_bin': return format(target_num, f'0{difficulty["bits"]}b')
    if m == 'bin_to_dec': return str(target_num)
    if m == 'dec_to_hex': return hex(target_num)[2:].upper()
    if m == 'hex_to_dec': return str(target_num)
    if m == 'bin_to_hex': return hex(target_num)[2:].upper()
    return ""

def get_question_display():
    m = mode['id']
    if m == 'dec_to_bin': return str(target_num), "decimal"
    if m == 'bin_to_dec': return format(target_num, f'0{difficulty["bits"]}b'), "binary"
    if m == 'dec_to_hex': return str(target_num), "decimal"
    if m == 'hex_to_dec': return hex(target_num)[2:].upper(), "hex"
    if m == 'bin_to_hex': return format(target_num, f'0{difficulty["bits"]}b'), "binary"
    return "", ""

def bits_to_int():
    n = difficulty['bits']
    val = 0
    for i in range(n):
        val += bits[i] * (2 ** (n - 1 - i))
    return val

def check_answer():
    global score, streak, lives, feedback, feedback_col, feedback_timer
    global correct_flash, wrong_flash, question_num, state, best_score
    m = mode['id']
    correct = False
    if m == 'dec_to_bin':
        correct = bits_to_int() == target_num
    else:
        ans = input_text.strip().upper()
        correct = (ans == correct_ans)

    if correct:
        bonus = 2 if hint_used == False else 1
        pts   = difficulty['points'] * bonus
        time_bonus = int((time_left / difficulty['time']) * 5)
        pts  += time_bonus
        score    += pts
        streak   += 1
        if streak >= 3:
            score += 5
        feedback      = f"+{pts}pts  {'STREAK x'+str(streak)+'! +5' if streak>=3 else ''}"
        feedback_col  = GREEN
        correct_flash = 20
        spawn_particles(W//2, 280, GREEN)
    else:
        lives   -= 1
        streak   = 0
        feedback = f"Wrong! Answer: {correct_ans}"
        feedback_col  = RED
        wrong_flash   = 20
        spawn_particles(W//2, 280, RED)

    feedback_timer = 90
    question_num  += 1
    best_score = max(best_score, score)

    if lives <= 0:
        state = STATE_GAMEOVER
        return
    if question_num >= MAX_QUESTIONS:
        state = STATE_RESULT
        return

    pygame.time.set_timer(pygame.USEREVENT, 800)

def spawn_particles(x, y, color):
    for _ in range(18):
        angle = random.uniform(0, 6.28)
        speed = random.uniform(2, 7)
        particle_list.append({
            'x': x, 'y': y,
            'vx': speed * __import__('math').cos(angle),
            'vy': speed * __import__('math').sin(angle),
            'life': random.randint(25, 50),
            'color': color,
            'r': random.randint(3, 7)
        })

def update_particles():
    for p in particle_list[:]:
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['vy'] += 0.2
        p['life'] -= 1
        if p['life'] <= 0:
            particle_list.remove(p)

def draw_particles():
    for p in particle_list:
        alpha = min(255, p['life'] * 6)
        col   = tuple(min(255, c) for c in p['color'])
        pygame.draw.circle(screen, col, (int(p['x']), int(p['y'])), p['r'])

def draw_panel(rect, col=PANEL, border=BORDER, radius=10):
    pygame.draw.rect(screen, col, rect, border_radius=radius)
    pygame.draw.rect(screen, border, rect, 1, border_radius=radius)

def draw_text(text, font, color, x, y, center=False):
    ts = font.render(text, True, color)
    if center:
        screen.blit(ts, (x - ts.get_width()//2, y))
    else:
        screen.blit(ts, (x, y))
    return ts.get_width(), ts.get_height()

def draw_menu():
    screen.fill(BG)
    draw_text("BINARY", F_HUGE, CYAN, W//2, 30, center=True)
    draw_text("CONVERTER GAME", F_BIG, BLUE, W//2, 92, center=True)
    draw_text("Best Score: " + str(best_score), F_MAIN, YELLOW, W//2, 135, center=True)

    # Mode selection
    draw_text("SELECT MODE", F_MED, GRAY, W//2, 175, center=True)
    my = 200
    for i, m in enumerate(MODES):
        selected = (m['id'] == mode['id'])
        col   = (20, 30, 55) if selected else PANEL
        bcol  = BLUE if selected else BORDER
        rect  = pygame.Rect(W//2-300, my, 600, 38)
        draw_panel(rect, col, bcol)
        tcol  = CYAN if selected else WHITE
        draw_text(m['label'], F_MAIN, tcol, W//2, my+10, center=True)
        if selected:
            draw_text("◄", F_MAIN, BLUE, W//2-285, my+10)
            draw_text("►", F_MAIN, BLUE, W//2+265, my+10)
        my += 46

    # Difficulty
    draw_text("DIFFICULTY", F_MED, GRAY, W//2, my+8, center=True)
    my += 35
    dx = W//2 - 200
    for i, d in enumerate(DIFFICULTIES):
        selected = (d['label'] == difficulty['label'])
        col  = (20, 30, 55) if selected else PANEL
        bcol = ORANGE if selected else BORDER
        rect = pygame.Rect(dx + i*140, my, 125, 40)
        draw_panel(rect, col, bcol)
        tcol = YELLOW if selected else WHITE
        draw_text(d['label'], F_MAIN, tcol, dx+i*140+62, my+11, center=True)
        draw_text(f"t:{d['time']}s", F_SMALL, GRAY, dx+i*140+62, my+28, center=True)
    my += 55

    # Info
    draw_text(mode['desc'], F_SMALL, GRAY, W//2, my, center=True)
    my += 30

    # Start
    rect = pygame.Rect(W//2-120, my, 240, 50)
    draw_panel(rect, (15, 40, 15), GREEN)
    draw_text("PRESS ENTER TO START", F_MAIN, GREEN, W//2, my+15, center=True)

    draw_text("Click options to select  |  Enter to start", F_SMALL, GRAY, W//2, H-25, center=True)

def draw_bits():
    global bit_rects
    bit_rects = []
    n = difficulty['bits']
    bw    = 64
    gap   = 10
    total = n * bw + (n-1) * gap
    sx    = W//2 - total//2
    by    = 300

    # Power labels
    for i in range(n):
        pw  = n - 1 - i
        bx  = sx + i * (bw + gap)
        lbl = F_SMALL.render(f"2^{pw}", True, GRAY)
        screen.blit(lbl, (bx + bw//2 - lbl.get_width()//2, by - 22))
        val_lbl = F_SMALL.render(str(2**pw), True, GRAY)
        screen.blit(val_lbl, (bx + bw//2 - val_lbl.get_width()//2, by - 8))

    for i in range(n):
        bx   = sx + i * (bw + gap)
        rect = pygame.Rect(bx, by, bw, bw)
        bit_rects.append(rect)
        on   = bits[i] == 1
        col  = BIT_ON if on else BIT_OFF
        bcol = BIT_BDR if on else BIT_BDR2
        draw_panel(rect, col, bcol, 8)
        digit_col = BG if on else GRAY
        draw_text(str(bits[i]), F_BIG, digit_col if on else GRAY, bx + bw//2, by + bw//2 - 14, center=True)

    # Current value
    val     = bits_to_int()
    val_col = GREEN if val == target_num else WHITE
    draw_text(f"= {val}", F_MED, val_col, W//2, by + bw + 12, center=True)

def draw_input_box():
    rect = pygame.Rect(W//2 - 200, 320, 400, 56)
    flash_col = PANEL
    if wrong_flash > 0:   flash_col = (40, 15, 15)
    if correct_flash > 0: flash_col = (15, 40, 15)
    draw_panel(rect, flash_col, BLUE, 10)
    display = input_text + ("█" if pygame.time.get_ticks()//500 % 2 == 0 else " ")
    draw_text(display, F_MONO, WHITE, W//2, rect.y + 14, center=True)

def draw_game():
    global wrong_flash, correct_flash, feedback_timer, time_left

    screen.fill(BG)
    update_particles()
    draw_particles()

    # Timer
    elapsed   = time.time() - time_start
    time_left = max(0, difficulty['time'] - elapsed)
    t_ratio   = time_left / difficulty['time']
    t_col     = GREEN if t_ratio > 0.5 else (YELLOW if t_ratio > 0.25 else RED)

    # Top bar
    draw_panel((0, 0, W, 58), (12, 16, 30), BORDER, 0)
    draw_text(f"Score: {score}", F_MED, YELLOW, 20, 16)
    draw_text(f"Q {question_num+1}/{MAX_QUESTIONS}", F_MED, GRAY, W//2, 16, center=True)
    draw_text(f"Best: {best_score}", F_MAIN, GRAY, W-160, 10)
    draw_text(f"Streak: {streak}", F_MAIN, ORANGE if streak>=3 else GRAY, W-160, 30)
    # Lives
    hearts = "♥ " * lives + "♡ " * (3 - lives)
    draw_text(hearts, F_MED, RED, W-300, 16)

    # Timer bar
    bar_w = int((W - 40) * t_ratio)
    pygame.draw.rect(screen, (20, 25, 40), (20, 52, W-40, 6), border_radius=3)
    if bar_w > 0:
        pygame.draw.rect(screen, t_col, (20, 52, bar_w, 6), border_radius=3)
    draw_text(f"{time_left:.1f}s", F_SMALL, t_col, W-55, 42)

    # Mode label
    draw_text(mode['label'], F_MAIN, BLUE, W//2, 72, center=True)
    draw_text(f"Difficulty: {difficulty['label']}  |  {mode['desc']}", F_SMALL, GRAY, W//2, 92, center=True)

    # Question
    qval, qtype = get_question_display()
    draw_text("Convert this " + qtype + ":", F_MAIN, GRAY, W//2, 125, center=True)

    flash_q = PANEL
    if wrong_flash > 0:   flash_q = (40, 15, 15)
    if correct_flash > 0: flash_q = (15, 40, 15)
    draw_panel((W//2-200, 148, 400, 80), flash_q, CYAN, 12)
    draw_text(qval, F_HUGE, CYAN, W//2, 158, center=True)

    # Input area
    m = mode['id']
    if m == 'dec_to_bin':
        draw_bits()
    else:
        draw_input_box()
        draw_text("Type your answer and press Enter", F_SMALL, GRAY, W//2, 386, center=True)

    # Hint
    if not hint_used:
        hint_rect = pygame.Rect(W//2-60, 430, 120, 32)
        draw_panel(hint_rect, PANEL, PURPLE, 6)
        draw_text("HINT (H)", F_SMALL, PURPLE, W//2, 439, center=True)
    else:
        draw_text(f"Hint: {correct_ans}", F_MAIN, PURPLE, W//2, 435, center=True)

    # Feedback
    if feedback_timer > 0:
        alpha = min(255, feedback_timer * 4)
        draw_text(feedback, F_MED, feedback_col, W//2, 478, center=True)
        feedback_timer -= 1

    # Bit values reminder for binary modes
    if m in ('bin_to_dec', 'bin_to_hex', 'dec_to_bin'):
        n = difficulty['bits']
        vals = "  ".join(str(2**(n-1-i)) for i in range(n))
        draw_text(f"Bit values: {vals}", F_SMALL, GRAY, W//2, H-35, center=True)

    if wrong_flash > 0:   wrong_flash   -= 1
    if correct_flash > 0: correct_flash -= 1

    if time_left <= 0:
        timeout()

def timeout():
    global lives, streak, feedback, feedback_col, feedback_timer
    global wrong_flash, question_num, state
    lives         -= 1
    streak         = 0
    feedback       = f"Time's up! Answer: {correct_ans}"
    feedback_col   = RED
    feedback_timer = 90
    wrong_flash    = 20
    spawn_particles(W//2, 280, RED)
    question_num  += 1
    if lives <= 0:
        state = STATE_GAMEOVER
        return
    if question_num >= MAX_QUESTIONS:
        state = STATE_RESULT
        return
    pygame.time.set_timer(pygame.USEREVENT, 800)

def draw_result(win):
    screen.fill(BG)
    title  = "ROUND COMPLETE!" if win else "GAME OVER"
    t_col  = YELLOW if win else RED
    draw_text(title, F_HUGE, t_col, W//2, 80, center=True)
    draw_panel((W//2-250, 180, 500, 260), PANEL, BORDER, 14)
    draw_text(f"Final Score:  {score}", F_BIG, YELLOW, W//2, 200, center=True)
    draw_text(f"Best Score:   {best_score}", F_MED, CYAN, W//2, 240, center=True)
    draw_text(f"Lives Left:   {'♥ '*lives}", F_MED, RED, W//2, 275, center=True)
    draw_text(f"Mode:         {mode['label']}", F_MAIN, GRAY, W//2, 315, center=True)
    draw_text(f"Difficulty:   {difficulty['label']}", F_MAIN, GRAY, W//2, 340, center=True)

    r1 = pygame.Rect(W//2-210, 470, 190, 48)
    r2 = pygame.Rect(W//2+20,  470, 190, 48)
    draw_panel(r1, (15,40,15), GREEN, 10)
    draw_panel(r2, (40,15,15), RED,   10)
    draw_text("PLAY AGAIN", F_MAIN, GREEN, W//2-115, 485, center=True)
    draw_text("MAIN MENU",  F_MAIN, RED,   W//2+115, 485, center=True)

# ── Main Loop ──────────────────────────────────────────────────────────────
def start_game():
    global score, lives, streak, question_num, state, particle_list
    score        = 0
    lives        = 3
    streak       = 0
    question_num = 0
    particle_list= []
    state        = STATE_PLAY
    new_question()

running = True
next_q_pending = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.USEREVENT:
            pygame.time.set_timer(pygame.USEREVENT, 0)
            if state == STATE_PLAY:
                new_question()

        if state == STATE_MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                # Mode buttons
                my_pos = 200
                for m in MODES:
                    rect = pygame.Rect(W//2-300, my_pos, 600, 38)
                    if rect.collidepoint(mx, my):
                        mode = m
                    my_pos += 46
                # Difficulty buttons
                my_pos += 43
                dx = W//2 - 200
                for i, d in enumerate(DIFFICULTIES):
                    rect = pygame.Rect(dx + i*140, my_pos, 125, 40)
                    if rect.collidepoint(mx, my):
                        difficulty = d
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                start_game()

        elif state == STATE_PLAY:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if mode['id'] == 'dec_to_bin':
                    for i, rect in enumerate(bit_rects):
                        if rect.collidepoint(mx, my):
                            bits[i] = 1 - bits[i]

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if mode['id'] == 'dec_to_bin':
                        check_answer()
                    else:
                        if input_text.strip():
                            check_answer()

                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]

                elif event.key == pygame.K_h:
                    hint_used = True

                elif event.key == pygame.K_SPACE and mode['id'] == 'dec_to_bin':
                    check_answer()

                else:
                    if mode['id'] != 'dec_to_bin' and len(input_text) < 12:
                        if event.unicode.isprintable():
                            input_text += event.unicode

        elif state in (STATE_RESULT, STATE_GAMEOVER):
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                r1 = pygame.Rect(W//2-210, 470, 190, 48)
                r2 = pygame.Rect(W//2+20,  470, 190, 48)
                if r1.collidepoint(mx, my):
                    start_game()
                if r2.collidepoint(mx, my):
                    state = STATE_MENU
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    start_game()
                if event.key == pygame.K_ESCAPE:
                    state = STATE_MENU

    # Draw
    if state == STATE_MENU:
        draw_menu()
    elif state == STATE_PLAY:
        draw_game()
    elif state in (STATE_RESULT, STATE_GAMEOVER):
        draw_result(state == STATE_RESULT)

    pygame.display.flip()
    clock.tick(60)