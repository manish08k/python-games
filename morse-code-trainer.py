import pygame
import sys
import random
import time
import math

pygame.init()

W, H = 1000, 680
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Morse Code Trainer")
clock = pygame.time.Clock()

# ── Colors ─────────────────────────────────────────────────────────────────
BG      = (8,  10, 18)
PANEL   = (14, 18, 32)
PANEL2  = (20, 26, 45)
BORDER  = (38, 52, 88)
WHITE   = (215, 222, 240)
GRAY    = (95, 110, 145)
LGRAY   = (140, 155, 185)
YELLOW  = (255, 205, 45)
GREEN   = (55, 205, 105)
RED     = (215, 60, 60)
BLUE    = (55, 140, 255)
CYAN    = (45, 205, 220)
PURPLE  = (170, 90, 255)
ORANGE  = (255, 148, 45)
AMBER   = (255, 176, 0)
DARK_G  = (12, 28, 16)
DARK_R  = (28, 10, 10)
DOT_COL = (45, 205, 220)
DASH_COL= (255, 148, 45)

F_HUGE  = pygame.font.SysFont("consolas", 48, bold=True)
F_BIG   = pygame.font.SysFont("consolas", 26, bold=True)
F_MED   = pygame.font.SysFont("consolas", 18, bold=True)
F_MAIN  = pygame.font.SysFont("consolas", 15)
F_SMALL = pygame.font.SysFont("consolas", 12)
F_MONO  = pygame.font.SysFont("consolas", 20, bold=True)
F_MORSE = pygame.font.SysFont("consolas", 28, bold=True)

# ── Morse Code Dictionary ───────────────────────────────────────────────────
MORSE = {
    'A':'.-',   'B':'-...', 'C':'-.-.', 'D':'-..', 'E':'.',
    'F':'..-.', 'G':'--.', 'H':'....', 'I':'..', 'J':'.---',
    'K':'-.-',  'L':'.-..', 'M':'--',  'N':'-.', 'O':'---',
    'P':'.--.', 'Q':'--.-', 'R':'.-.', 'S':'...', 'T':'-',
    'U':'..-',  'V':'...-', 'W':'.--', 'X':'-..-', 'Y':'-.--',
    'Z':'--..',
    '0':'-----','1':'.----','2':'..---','3':'...--','4':'....-',
    '5':'.....','6':'-....','7':'--...','8':'---..','9':'----.',
    '.':'.-.-.-',',':'--..--','?':'..--..','!':'-.-.--',
    '/':'-..-.',  '-':'-....-',
}
MORSE_REV = {v: k for k, v in MORSE.items()}

ALPHABET  = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
DIGITS    = list('0123456789')
COMMON    = list('ETAOINSHRDLU')

WORDS = [
    'CAT','DOG','SOS','HELP','CODE','MOON','STAR','RAIN',
    'FIRE','WIND','BIRD','TREE','SHIP','WAVE','SALT','GOLD',
    'HERO','DARK','DAWN','ECHO','FROG','GLOW','HIVE','IRIS',
]

MODES = [
    {'id':'learn',    'label':'Learn',      'icon':'📖', 'desc':'Study the morse code chart'},
    {'id':'char',     'label':'Char Quiz',  'icon':'🔤', 'desc':'Identify morse for single characters'},
    {'id':'decode',   'label':'Decode',     'icon':'🔍', 'desc':'Type the letter from morse shown'},
    {'id':'encode',   'label':'Encode',     'icon':'✏', 'desc':'Type morse code for the character'},
    {'id':'word',     'label':'Word Quiz',  'icon':'📝', 'desc':'Decode full morse code words'},
    {'id':'speed',    'label':'Speed Run',  'icon':'⚡', 'desc':'Answer 20 questions as fast as possible'},
    {'id':'listen',   'label':'Listen',     'icon':'🔊', 'desc':'Hear morse tones and decode them'},
]

DIFFS = [
    {'label':'Letters', 'pool': ALPHABET,          'time':25},
    {'label':'Numbers', 'pool': DIGITS,             'time':20},
    {'label':'Mixed',   'pool': ALPHABET+DIGITS,    'time':18},
    {'label':'Common',  'pool': COMMON,             'time':15},
]

ST_MENU   = 'menu'
ST_LEARN  = 'learn'
ST_PLAY   = 'play'
ST_SPEED  = 'speed'
ST_OVER   = 'over'
ST_LISTEN = 'listen'

# ── Audio (morse tones) ────────────────────────────────────────────────────
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

def make_tone(freq=650, duration=0.08, vol=0.5):
    sr    = 44100
    n     = int(sr * duration)
    buf   = bytes([
        int(127 + 127 * vol * math.sin(2 * math.pi * freq * t / sr))
        for t in range(n)
    ])
    snd   = pygame.mixer.Sound(buffer=buf)
    return snd

DOT_SND  = make_tone(650, 0.08)
DASH_SND = make_tone(650, 0.24)

def play_morse_audio(morse_str):
    for ch in morse_str:
        if ch == '.':
            DOT_SND.play()
            pygame.time.delay(130)
        elif ch == '-':
            DASH_SND.play()
            pygame.time.delay(320)
        elif ch == ' ':
            pygame.time.delay(200)

# ── State ──────────────────────────────────────────────────────────────────
app_state    = ST_MENU
cur_mode     = MODES[0]
cur_diff     = DIFFS[0]
score        = 0
best_score   = 0
lives        = 3
streak       = 0
question_num = 0
MAX_Q        = 20
target_char  = ''
target_morse = ''
input_text   = ''
feedback     = ''
fb_col       = WHITE
fb_timer     = 0
time_left    = 0
time_start   = 0
wrong_flash  = 0
right_flash  = 0
hint_shown   = False
particles    = []
learn_page   = 0
speed_times  = []
speed_start  = 0
listen_morse = ''
listen_playing = False
options      = []   # for char quiz MCQ
correct_opt  = 0

# ── Helpers ────────────────────────────────────────────────────────────────
def txt(text, font, color, x, y, center=False, right=False):
    s = font.render(str(text), True, color)
    if center: x -= s.get_width()//2
    if right:  x -= s.get_width()
    screen.blit(s, (x, y))
    return s.get_width(), s.get_height()

def panel(rect, col=PANEL, border=BORDER, r=10):
    pygame.draw.rect(screen, col, rect, border_radius=r)
    pygame.draw.rect(screen, border, rect, 1, border_radius=r)

def spawn_particles(x, y, col):
    for _ in range(22):
        a = random.uniform(0, 6.28)
        s = random.uniform(2.5, 8)
        particles.append({
            'x':x,'y':y,
            'vx':s*math.cos(a),'vy':s*math.sin(a),
            'life':random.randint(28,55),
            'col':col,'r':random.randint(3,7)
        })

def update_draw_particles():
    for p in particles[:]:
        p['x']+=p['vx']; p['y']+=p['vy']; p['vy']+=0.25; p['life']-=1
        if p['life']<=0: particles.remove(p); continue
        pygame.draw.circle(screen, p['col'], (int(p['x']),int(p['y'])), p['r'])

def draw_morse_symbols(morse_str, cx, cy, big=False):
    sym_w  = 18 if big else 12
    dash_w = 36 if big else 24
    gap    = 8  if big else 5
    h      = 10 if big else 6
    parts  = []
    for ch in morse_str:
        parts.append(('dash' if ch=='-' else 'dot'))
    total  = sum(dash_w if p=='dash' else sym_w for p in parts) + gap*(len(parts)-1)
    x      = cx - total//2
    for p in parts:
        w  = dash_w if p=='dash' else sym_w
        col= DASH_COL if p=='dash' else DOT_COL
        r  = h//2
        pygame.draw.rect(screen, col, (x, cy-h//2, w, h), border_radius=r)
        x += w + gap

def new_question():
    global target_char, target_morse, input_text, feedback
    global fb_timer, time_left, time_start, hint_shown
    global options, correct_opt, listen_morse, listen_playing

    pool         = cur_diff['pool']
    target_char  = random.choice(pool)
    target_morse = MORSE[target_char]
    input_text   = ''
    feedback     = ''
    fb_timer     = 0
    hint_shown   = False
    time_left    = cur_diff['time']
    time_start   = time.time()

    if cur_mode['id'] == 'char':
        wrong_opts = random.sample([c for c in pool if c!=target_char], 3)
        all_opts   = wrong_opts + [target_char]
        random.shuffle(all_opts)
        options    = all_opts
        correct_opt= all_opts.index(target_char)

    if cur_mode['id'] == 'listen':
        listen_morse   = target_morse
        listen_playing = False

def check_answer(ans):
    global score, streak, lives, feedback, fb_col, fb_timer
    global wrong_flash, right_flash, question_num, app_state, best_score

    ans    = ans.strip().upper()
    m      = cur_mode['id']
    correct= False

    if m == 'decode':
        correct = (ans == target_char)
    elif m == 'encode':
        correct = (ans == target_morse)
    elif m == 'word':
        correct = (ans == target_char)
    elif m == 'char':
        correct = (ans == target_char)
    elif m == 'speed':
        correct = (ans == target_char)
    elif m == 'listen':
        correct = (ans == target_char)

    if correct:
        pts        = 10 + (5 if streak>=3 else 0) + (0 if hint_shown else 3)
        score     += pts
        streak    += 1
        feedback   = f"+{pts}  {'🔥STREAK x'+str(streak)+'!' if streak>=3 else 'Correct!'}"
        fb_col     = GREEN
        right_flash= 18
        spawn_particles(W//2, H//2, GREEN)
    else:
        lives    -= 1
        streak    = 0
        feedback  = f"Wrong!  Answer: {target_char}  ({target_morse})"
        fb_col    = RED
        wrong_flash= 18
        spawn_particles(W//2, H//2, RED)

    fb_timer      = 90
    question_num += 1
    best_score    = max(best_score, score)

    if m == 'speed':
        speed_times.append(time.time() - time_start)

    if lives <= 0 or question_num >= MAX_Q:
        app_state = ST_OVER
        return

    pygame.time.set_timer(pygame.USEREVENT, 700)

def timeout_q():
    global lives, streak, feedback, fb_col, fb_timer, wrong_flash, question_num, app_state
    lives      -= 1
    streak      = 0
    feedback    = f"Time's up!  Answer: {target_char}  ({target_morse})"
    fb_col      = RED
    fb_timer    = 90
    wrong_flash = 18
    question_num+=1
    spawn_particles(W//2, H//2, RED)
    if lives<=0 or question_num>=MAX_Q:
        app_state = ST_OVER; return
    pygame.time.set_timer(pygame.USEREVENT, 700)

# ── Draw Menu ──────────────────────────────────────────────────────────────
def draw_menu():
    screen.fill(BG)
    # Title
    panel((W//2-260, 12, 520, 70), (12,16,30), CYAN, 14)
    txt("MORSE CODE TRAINER", F_BIG, CYAN, W//2, 28, center=True)
    txt("Master the dots and dashes", F_SMALL, GRAY, W//2, 58, center=True)

    # Modes grid
    txt("SELECT MODE", F_MED, GRAY, W//2, 100, center=True)
    cols, rows = 4, 2
    mw, mh     = 210, 78
    gx         = W//2 - (cols*mw + (cols-1)*10)//2
    gy         = 125
    for i, m in enumerate(MODES):
        c   = i % cols
        r   = i // cols
        rx  = gx + c*(mw+10)
        ry  = gy + r*(mh+10)
        sel = (m['id'] == cur_mode['id'])
        bc  = CYAN if sel else BORDER
        bg  = (18,28,50) if sel else PANEL
        panel((rx, ry, mw, mh), bg, bc, 10)
        txt(m['icon']+" "+m['label'], F_MED, CYAN if sel else WHITE, rx+mw//2, ry+12, center=True)
        # wrap desc
        words2  = m['desc'].split()
        line1   = ' '.join(words2[:4])
        line2   = ' '.join(words2[4:])
        txt(line1, F_SMALL, LGRAY, rx+mw//2, ry+38, center=True)
        if line2: txt(line2, F_SMALL, LGRAY, rx+mw//2, ry+52, center=True)

    # Difficulty
    gy2 = gy + 2*(mh+10) + 16
    txt("POOL / DIFFICULTY", F_MED, GRAY, W//2, gy2, center=True)
    dw  = 185
    dx  = W//2 - (len(DIFFS)*dw + (len(DIFFS)-1)*10)//2
    for i, d in enumerate(DIFFS):
        rx  = dx + i*(dw+10)
        ry  = gy2+28
        sel = (d['label']==cur_diff['label'])
        panel((rx, ry, dw, 50), (18,28,50) if sel else PANEL, ORANGE if sel else BORDER, 8)
        txt(d['label'], F_MAIN, YELLOW if sel else WHITE, rx+dw//2, ry+8, center=True)
        txt(f"timer: {d['time']}s", F_SMALL, GRAY, rx+dw//2, ry+28, center=True)

    # Start
    gy3 = gy2 + 100
    panel((W//2-140, gy3, 280, 52), DARK_G, GREEN, 12)
    txt("PRESS  ENTER  TO  START", F_MAIN, GREEN, W//2, gy3+16, center=True)
    txt("Click options to select mode/difficulty", F_SMALL, GRAY, W//2, H-20, center=True)

# ── Draw Learn ─────────────────────────────────────────────────────────────
def draw_learn():
    screen.fill(BG)
    panel((0,0,W,50), (12,16,30), BORDER, 0)
    txt("MORSE CODE REFERENCE CHART", F_MED, YELLOW, W//2, 14, center=True)
    txt("ESC = menu", F_SMALL, GRAY, W-90, 18)

    keys    = ALPHABET + DIGITS
    per_row = 9
    cw, ch  = 100, 52
    sx      = W//2 - (per_row*cw + (per_row-1)*4)//2
    sy      = 65
    for i, k in enumerate(keys):
        c  = i % per_row
        r  = i // per_row
        rx = sx + c*(cw+4)
        ry = sy + r*(ch+4)
        m  = MORSE[k]
        panel((rx, ry, cw, ch), PANEL2, BORDER, 7)
        txt(k,    F_MED,  YELLOW, rx+cw//2, ry+5,  center=True)
        txt(m,    F_SMALL, CYAN,  rx+cw//2, ry+26, center=True)
        # mini symbols
        draw_morse_symbols(m, rx+cw//2, ry+44)

    txt("← ESC to return to menu →", F_SMALL, GRAY, W//2, H-18, center=True)

# ── Draw Play ──────────────────────────────────────────────────────────────
def draw_play():
    global wrong_flash, right_flash, fb_timer, time_left

    screen.fill(BG)
    update_draw_particles()

    elapsed    = time.time() - time_start
    time_left  = max(0.0, cur_diff['time'] - elapsed)
    t_ratio    = time_left / cur_diff['time']
    t_col      = GREEN if t_ratio>0.5 else (YELLOW if t_ratio>0.25 else RED)

    # Top bar
    panel((0,0,W,54), (11,15,28), BORDER, 0)
    txt(f"Score: {score}", F_MED, YELLOW, 18, 16)
    txt(cur_mode['label'], F_MED, CYAN, W//2, 16, center=True)
    txt(f"Q {question_num+1}/{MAX_Q}", F_MAIN, GRAY, W//2, 38, center=True)
    hearts = "♥ "*lives + "♡ "*(3-lives)
    txt(hearts, F_MED, RED, W-220, 16)
    txt(f"Best:{best_score}", F_SMALL, GRAY, W-85, 16)
    if streak>=3:
        txt(f"🔥x{streak}", F_MED, ORANGE, W-85, 34)

    # Timer bar
    bw = int((W-40)*t_ratio)
    pygame.draw.rect(screen, (20,25,42), (20,52,W-40,5), border_radius=3)
    if bw>0: pygame.draw.rect(screen, t_col, (20,52,bw,5), border_radius=3)
    txt(f"{time_left:.1f}s", F_SMALL, t_col, W-45, 42)

    m = cur_mode['id']

    # Flash background
    if wrong_flash>0:
        ov = pygame.Surface((W,H), pygame.SRCALPHA)
        ov.fill((180,20,20, min(80, wrong_flash*6)))
        screen.blit(ov,(0,0))
        wrong_flash-=1
    if right_flash>0:
        ov = pygame.Surface((W,H), pygame.SRCALPHA)
        ov.fill((20,180,60, min(70, right_flash*5)))
        screen.blit(ov,(0,0))
        right_flash-=1

    # ── DECODE: show morse, type letter ──
    if m in ('decode','listen'):
        txt("Decode this Morse Code:", F_MAIN, GRAY, W//2, 80, center=True)
        q_morse = listen_morse if m=='listen' else target_morse
        panel((W//2-280, 110, 560, 100), PANEL2, CYAN, 14)
        txt(q_morse, F_MORSE, AMBER, W//2, 122, center=True)
        draw_morse_symbols(q_morse, W//2, 188, big=True)

        if m=='listen':
            panel((W//2-80,220,160,38), PANEL, BLUE, 8)
            txt("▶ SPACE to play", F_SMALL, BLUE, W//2, 230, center=True)

        txt("Type the character:", F_MAIN, GRAY, W//2, 275, center=True)
        bc = (18,38,18) if right_flash>0 else ((38,14,14) if wrong_flash>0 else PANEL2)
        panel((W//2-100,298,200,52), bc, CYAN, 10)
        disp = input_text.upper() + ("█" if pygame.time.get_ticks()//500%2==0 else " ")
        txt(disp, F_HUGE, WHITE, W//2, 308, center=True)

    # ── ENCODE: show letter, type morse ──
    elif m=='encode':
        txt("Encode this character to Morse:", F_MAIN, GRAY, W//2, 80, center=True)
        panel((W//2-120,105,240,110), PANEL2, YELLOW, 14)
        txt(target_char, F_HUGE, YELLOW, W//2, 118, center=True)
        txt("character", F_SMALL, GRAY, W//2, 188, center=True)
        txt("Type morse  (dot=.  dash=-  space between):", F_MAIN, GRAY, W//2, 242, center=True)
        bc = (18,38,18) if right_flash>0 else ((38,14,14) if wrong_flash>0 else PANEL2)
        panel((W//2-240,265,480,52), bc, AMBER, 10)
        disp = input_text + ("█" if pygame.time.get_ticks()//500%2==0 else " ")
        txt(disp, F_MORSE, AMBER, W//2, 277, center=True)
        if hint_shown:
            txt(f"Hint: {target_morse}", F_MAIN, PURPLE, W//2, 335, center=True)

    # ── CHAR QUIZ: show morse, pick letter (MCQ) ──
    elif m=='char':
        txt("Which character is this?", F_MAIN, GRAY, W//2, 80, center=True)
        panel((W//2-250,105,500,100), PANEL2, CYAN, 14)
        txt(target_morse, F_MORSE, AMBER, W//2, 118, center=True)
        draw_morse_symbols(target_morse, W//2, 185, big=True)
        # Options
        ow,oh = 160,60
        ox = W//2 - (2*ow+20)//2
        for i,op in enumerate(options):
            c   = i%2; r = i//2
            rx  = ox + c*(ow+20)
            ry  = 225 + r*(oh+12)
            sel_col = PANEL2
            brd = BORDER
            panel((rx,ry,ow,oh), sel_col, brd, 10)
            txt(op, F_BIG, WHITE, rx+ow//2, ry+15, center=True)
            txt(f"Press {i+1}", F_SMALL, GRAY, rx+ow//2, ry+40, center=True)

    # ── WORD: show full word morse, type word ──
    elif m=='word':
        txt("Decode the full word:", F_MAIN, GRAY, W//2, 80, center=True)
        wm = ' / '.join(MORSE[c] for c in target_char)
        panel((W//2-380,105,760,80), PANEL2, CYAN, 12)
        # wrap if long
        txt(wm, F_MAIN, AMBER, W//2, 128, center=True)
        txt("(/ = space between letters)", F_SMALL, GRAY, W//2, 175, center=True)
        txt("Type the word:", F_MAIN, GRAY, W//2, 215, center=True)
        bc = (18,38,18) if right_flash>0 else ((38,14,14) if wrong_flash>0 else PANEL2)
        panel((W//2-200,238,400,56), bc, CYAN, 10)
        disp = input_text.upper()+("█" if pygame.time.get_ticks()//500%2==0 else " ")
        txt(disp, F_BIG, WHITE, W//2, 252, center=True)

    # ── SPEED: decode fast ──
    elif m=='speed':
        txt(f"⚡ SPEED RUN — {MAX_Q} questions, go fast!", F_MAIN, ORANGE, W//2, 80, center=True)
        panel((W//2-250,105,500,100), PANEL2, ORANGE, 14)
        txt(target_morse, F_MORSE, AMBER, W//2, 118, center=True)
        draw_morse_symbols(target_morse, W//2, 185, big=True)
        txt("Type character:", F_MAIN, GRAY, W//2, 240, center=True)
        bc = (18,38,18) if right_flash>0 else ((38,14,14) if wrong_flash>0 else PANEL2)
        panel((W//2-100,262,200,52), bc, ORANGE, 10)
        disp = input_text.upper()+("█" if pygame.time.get_ticks()//500%2==0 else " ")
        txt(disp, F_HUGE, WHITE, W//2, 272, center=True)

    # Hint button
    if m in ('encode','decode') and not hint_shown:
        panel((W//2-55, H-95, 110, 30), PANEL, PURPLE, 7)
        txt("H = Hint", F_SMALL, PURPLE, W//2, H-89, center=True)

    # Feedback
    if fb_timer>0:
        txt(feedback, F_MED, fb_col, W//2, H-55, center=True)
        fb_timer -= 1

    # Morse reference strip at bottom
    panel((0, H-32, W, 32), (11,14,26), BORDER, 0)
    ref = "A=.-  E=.  I=..  O=---  S=...  T=-  H=....  R=.-.  N=-.  M=--"
    txt(ref, F_SMALL, GRAY, W//2, H-24, center=True)

    if time_left<=0:
        timeout_q()

# ── Draw Game Over ──────────────────────────────────────────────────────────
def draw_over():
    screen.fill(BG)
    panel((W//2-310, 60, 620, 70), (16,16,30), YELLOW, 14)
    txt("SESSION COMPLETE", F_BIG, YELLOW, W//2, 78, center=True)

    panel((W//2-280, 150, 560, 280), PANEL, BORDER, 14)
    txt(f"Score:       {score}", F_MED, YELLOW, W//2, 170, center=True)
    txt(f"Best Score:  {best_score}", F_MED, CYAN,   W//2, 205, center=True)
    txt(f"Mode:        {cur_mode['label']}", F_MAIN, WHITE, W//2, 245, center=True)
    txt(f"Pool:        {cur_diff['label']}", F_MAIN, WHITE, W//2, 270, center=True)
    txt(f"Lives left:  {'♥ '*lives}", F_MAIN, RED, W//2, 300, center=True)
    if speed_times:
        avg = sum(speed_times)/len(speed_times)
        txt(f"Avg time:    {avg:.2f}s per question", F_MAIN, ORANGE, W//2, 328, center=True)
    txt(f"Streak peak: {streak}", F_MAIN, ORANGE, W//2, 356, center=True)

    panel((W//2-220,460,200,50), DARK_G, GREEN, 10)
    txt("ENTER = Play Again", F_MAIN, GREEN, W//2-120, 475)
    panel((W//2+20,460,200,50), DARK_R, RED, 10)
    txt("ESC = Main Menu", F_MAIN, RED, W//2+30, 475)

# ── Start game ─────────────────────────────────────────────────────────────
def start_game():
    global score,lives,streak,question_num,app_state,particles,speed_times,speed_start
    score        = 0
    lives        = 3
    streak       = 0
    question_num = 0
    particles    = []
    speed_times  = []
    speed_start  = time.time()
    if cur_mode['id']=='word':
        cur_diff['pool'] = WORDS  # type: ignore
    app_state = ST_PLAY if cur_mode['id']!='learn' else ST_LEARN
    if app_state==ST_PLAY:
        new_question()

# ── Main Loop ──────────────────────────────────────────────────────────────
while True:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type==pygame.USEREVENT:
            pygame.time.set_timer(pygame.USEREVENT,0)
            if app_state==ST_PLAY:
                new_question()

        # ── MENU events ──
        if app_state==ST_MENU:
            if event.type==pygame.MOUSEBUTTONDOWN:
                mx,my=event.pos
                # modes
                cols2,mw2,mh2=4,210,78
                gx2=W//2-(cols2*mw2+(cols2-1)*10)//2
                gy2=125
                for i,m in enumerate(MODES):
                    c=i%cols2; r=i//cols2
                    rx=gx2+c*(mw2+10); ry=gy2+r*(mh2+10)
                    if pygame.Rect(rx,ry,mw2,mh2).collidepoint(mx,my):
                        cur_mode=m
                # diffs
                gy3=gy2+2*(mh2+10)+16+28
                dw2=185
                dx2=W//2-(len(DIFFS)*dw2+(len(DIFFS)-1)*10)//2
                for i,d in enumerate(DIFFS):
                    rx=dx2+i*(dw2+10)
                    if pygame.Rect(rx,gy3,dw2,50).collidepoint(mx,my):
                        cur_diff=d
            if event.type==pygame.KEYDOWN and event.key==pygame.K_RETURN:
                start_game()

        # ── LEARN events ──
        elif app_state==ST_LEARN:
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
                app_state=ST_MENU

        # ── PLAY events ──
        elif app_state==ST_PLAY:
            m=cur_mode['id']
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    app_state=ST_MENU

                elif m=='char':
                    if event.key in (pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4):
                        idx=event.key-pygame.K_1
                        if idx<len(options):
                            check_answer(options[idx])

                elif m=='listen':
                    if event.key==pygame.K_SPACE:
                        play_morse_audio(listen_morse)
                    elif event.key==pygame.K_RETURN:
                        if input_text.strip():
                            check_answer(input_text)
                    elif event.key==pygame.K_BACKSPACE:
                        input_text=input_text[:-1]
                    elif event.key==pygame.K_h and not hint_shown:
                        hint_shown=True
                    else:
                        if len(input_text)<6 and event.unicode.isalpha():
                            input_text+=event.unicode

                elif m in ('decode','speed'):
                    if event.key==pygame.K_RETURN and input_text.strip():
                        check_answer(input_text)
                    elif event.key==pygame.K_BACKSPACE:
                        input_text=input_text[:-1]
                    elif event.key==pygame.K_h and not hint_shown:
                        hint_shown=True
                    else:
                        if len(input_text)<4 and event.unicode.isalpha():
                            input_text+=event.unicode

                elif m=='encode':
                    if event.key==pygame.K_RETURN and input_text.strip():
                        check_answer(input_text)
                    elif event.key==pygame.K_BACKSPACE:
                        input_text=input_text[:-1]
                    elif event.key==pygame.K_h and not hint_shown:
                        hint_shown=True
                    elif event.unicode in ('.','-',' '):
                        if len(input_text)<12:
                            input_text+=event.unicode

                elif m=='word':
                    if event.key==pygame.K_RETURN and input_text.strip():
                        check_answer(input_text)
                    elif event.key==pygame.K_BACKSPACE:
                        input_text=input_text[:-1]
                    else:
                        if len(input_text)<10 and event.unicode.isalpha():
                            input_text+=event.unicode

        # ── GAME OVER events ──
        elif app_state==ST_OVER:
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_RETURN:
                    start_game()
                if event.key==pygame.K_ESCAPE:
                    app_state=ST_MENU

    # ── Draw ──
    if app_state==ST_MENU:
        draw_menu()
    elif app_state==ST_LEARN:
        draw_learn()
    elif app_state==ST_PLAY:
        draw_play()
    elif app_state==ST_OVER:
        draw_over()

    pygame.display.flip()
    clock.tick(60)