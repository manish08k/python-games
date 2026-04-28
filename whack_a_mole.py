"""
Whack-a-Mole — Python + Pygame
Run: python whack_a_mole.py
Requires: pip install pygame numpy
"""

import pygame
import sys
import math
import random
import numpy as np

WIDTH, HEIGHT = 600, 700
FPS = 60

BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
BROWN   = (101, 67,  33)
DKBROWN = (70,  40,  10)
GREEN   = (60,  180, 60)
DKGREEN = (30,  120, 30)
YELLOW  = (255, 220, 0)
RED     = (220, 40,  40)
ORANGE  = (255, 140, 0)
PINK    = (255, 160, 180)
CREAM   = (255, 240, 210)
GREY    = (130, 130, 130)
DKGREY  = (40,  40,  40)
CYAN    = (0,   210, 255)
PURPLE  = (160, 60,  220)
GOLD    = (255, 200, 0)
SKY     = (100, 180, 255)
GRASS   = (80,  200, 80)

RATE = 22050

def _buf(arr, vol=0.55):
    a = np.clip(arr * vol * 32767, -32767, 32767).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack([a, a]))

def snd_whack():
    t = np.linspace(0, 0.12, int(RATE*0.12))
    s = np.random.uniform(-1,1,len(t)) * np.exp(-18*t/0.12)
    tone = np.sin(2*np.pi*180*t) * np.exp(-12*t/0.12) * 0.5
    return _buf(s*0.6 + tone)

def snd_miss():
    t = np.linspace(0, 0.18, int(RATE*0.18))
    f = np.linspace(600, 200, len(t))
    s = np.sin(2*np.pi*f*t) * np.linspace(0.4, 0, len(t))
    return _buf(s)

def snd_appear():
    t = np.linspace(0, 0.08, int(RATE*0.08))
    f = np.linspace(300, 500, len(t))
    s = np.sin(2*np.pi*f*t) * np.linspace(0, 0.4, len(t))
    return _buf(s)

def snd_golden():
    t = np.linspace(0, 0.2, int(RATE*0.2))
    f = np.linspace(600, 1000, len(t))
    s = np.sin(2*np.pi*f*t) * np.linspace(0.5, 0, len(t))
    return _buf(s)

def snd_bomb():
    t = np.linspace(0, 0.3, int(RATE*0.3))
    noise = np.random.uniform(-1,1,len(t))
    env = np.exp(-6*t/0.3)
    tone = np.sin(2*np.pi*80*t)*0.4
    return _buf((noise*0.6+tone)*env)

def snd_gameover():
    t = np.linspace(0, 0.5, int(RATE*0.5))
    f = np.linspace(400, 100, len(t))
    s = np.sin(2*np.pi*f*t) * np.exp(-3*t/0.5)
    return _buf(s)

def snd_levelup():
    t = np.linspace(0, 0.35, int(RATE*0.35))
    f1 = np.sin(2*np.pi*523*t)
    f2 = np.sin(2*np.pi*659*t)
    f3 = np.sin(2*np.pi*784*t)
    s = (f1 + f2 + f3) / 3 * np.linspace(0.5, 0, len(t))
    return _buf(s)

# ── Particle ───────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color, speed=4, life=35, size=5):
        a = random.uniform(0, math.pi*2)
        s = random.uniform(speed*0.4, speed)
        self.x, self.y = x, y
        self.vx = math.cos(a)*s
        self.vy = math.sin(a)*s - random.uniform(1,3)
        self.color = color
        self.life = self.ml = life + random.randint(-8,8)
        self.size = size + random.uniform(-1,2)
        self.gravity = 0.18

    def update(self):
        self.vx *= 0.92
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surf):
        a = max(0, self.life/self.ml)
        r,g,b = self.color
        c = (int(r*a), int(g*a), int(b*a))
        sz = max(1, int(self.size * a))
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), sz)

class StarParticle:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx = random.uniform(-3,3)
        self.vy = random.uniform(-5,-1)
        self.life = self.ml = random.randint(30,50)
        self.color = random.choice([GOLD, YELLOW, WHITE, ORANGE])
        self.angle = random.uniform(0, 360)
        self.spin  = random.uniform(-8, 8)
        self.size  = random.uniform(6,12)

    def update(self):
        self.vy += 0.15
        self.x += self.vx; self.y += self.vy
        self.angle += self.spin
        self.life -= 1

    def draw(self, surf):
        a = self.life/self.ml
        r,g,b = self.color
        c = (int(r*a),int(g*a),int(b*a))
        cx, cy = int(self.x), int(self.y)
        s = self.size * a
        for i in range(5):
            ang = math.radians(self.angle + i*72)
            ang2= math.radians(self.angle + i*72 + 36)
            ox,oy = math.cos(ang)*s, math.sin(ang)*s
            ix,iy = math.cos(ang2)*s*0.4, math.sin(ang2)*s*0.4
            if i == 0:
                pts = []
            pts += [(cx+ox, cy+oy), (cx+ix, cy+iy)]
        if len(pts) >= 6:
            pygame.draw.polygon(surf, c, pts, 0)

# ── FloatingText ───────────────────────────────────────────────────────────────
class FloatingText:
    def __init__(self, x, y, text, color=YELLOW, size=28):
        self.x, self.y = float(x), float(y)
        self.text = text
        self.color = color
        self.life = self.ml = 55
        self.font = pygame.font.SysFont("Courier", size, bold=True)

    def update(self):
        self.y -= 1.2
        self.life -= 1

    def draw(self, surf):
        a = self.life/self.ml
        r,g,b = self.color
        c = (int(r*a), int(g*a), int(b*a))
        t = self.font.render(self.text, True, c)
        surf.blit(t, (int(self.x) - t.get_width()//2, int(self.y)))

# ── Mole types ─────────────────────────────────────────────────────────────────
NORMAL = 'normal'
GOLDEN = 'golden'
BOMB   = 'bomb'
SPEEDY = 'speedy'
HARD   = 'hard'

MOLE_DATA = {
    NORMAL: dict(pts=10,  color=BROWN,  hat=False, bomb=False, hp=1),
    GOLDEN: dict(pts=50,  color=GOLD,   hat=True,  bomb=False, hp=1),
    BOMB:   dict(pts=-30, color=RED,    hat=False, bomb=True,  hp=1),
    SPEEDY: dict(pts=20,  color=ORANGE, hat=False, bomb=False, hp=1),
    HARD:   dict(pts=30,  color=PURPLE, hat=True,  bomb=False, hp=2),
}

# ── Hole / Mole ────────────────────────────────────────────────────────────────
class Hole:
    RISE_SPD = 4.5
    HIDE_SPD = 6.0

    def __init__(self, cx, cy, idx):
        self.cx, self.cy = cx, cy
        self.idx = idx
        self.rx  = 48
        self.ry  = 22
        self.mole_h = 56

        self.active  = False
        self.kind    = NORMAL
        self.hp      = 1
        self.offset  = self.mole_h   # 0 = fully up, mole_h = hidden
        self.state   = 'hidden'      # hidden | rising | up | hiding | hit
        self.up_timer = 0
        self.hit_timer = 0
        self.wobble = 0
        self.eyes_open = True
        self.blink_timer = random.randint(60, 120)

    def spawn(self, kind, up_time):
        self.kind     = kind
        self.hp       = MOLE_DATA[kind]['hp']
        self.active   = True
        self.state    = 'rising'
        self.up_timer = up_time
        self.offset   = self.mole_h
        self.wobble   = 0

    def whack(self):
        if self.state in ('up','rising') and self.active:
            self.hp -= 1
            self.wobble = 10
            if self.hp <= 0:
                self.state    = 'hit'
                self.hit_timer = 14
                self.active   = False
                return True
        return False

    def update(self):
        spd = self.RISE_SPD
        if self.kind == SPEEDY: spd = 7.5
        hide_spd = self.HIDE_SPD
        if self.kind == SPEEDY: hide_spd = 9.0

        if self.state == 'rising':
            self.offset = max(0, self.offset - spd)
            if self.offset == 0:
                self.state = 'up'
        elif self.state == 'up':
            self.up_timer -= 1
            if self.up_timer <= 0:
                self.state = 'hiding'
        elif self.state == 'hiding':
            self.offset = min(self.mole_h, self.offset + hide_spd)
            if self.offset >= self.mole_h:
                self.state  = 'hidden'
                self.active = False
        elif self.state == 'hit':
            self.hit_timer -= 1
            self.offset = min(self.mole_h, self.offset + hide_spd*1.5)
            if self.hit_timer <= 0:
                self.state = 'hidden'

        if self.wobble > 0: self.wobble -= 1

        self.blink_timer -= 1
        if self.blink_timer <= 0:
            self.eyes_open = not self.eyes_open
            self.blink_timer = 6 if not self.eyes_open else random.randint(60,140)

    def draw(self, surf):
        # Hole shadow
        pygame.draw.ellipse(surf, (15,10,5),
            (self.cx-self.rx-3, self.cy-self.ry-3, (self.rx+3)*2, (self.ry+3)*2))
        # Hole
        pygame.draw.ellipse(surf, DKBROWN,
            (self.cx-self.rx, self.cy-self.ry, self.rx*2, self.ry*2))
        pygame.draw.ellipse(surf, BLACK,
            (self.cx-self.rx+4, self.cy-self.ry+4, (self.rx-4)*2, (self.ry-4)*2))

        if self.state == 'hidden': return

        data = MOLE_DATA[self.kind]
        color = data['color']

        my = self.cy - self.ry + 6 + self.offset - self.mole_h
        wobble_x = int(math.sin(self.wobble * 0.8) * 3) if self.wobble > 0 else 0

        cx = self.cx + wobble_x

        # Clip drawing to hole top
        clip_y = self.cy - self.ry + 6
        old_clip = surf.get_clip()
        surf.set_clip(pygame.Rect(0, 0, WIDTH, clip_y + 4))

        # Body
        body_color = color
        if self.state == 'hit':
            body_color = WHITE
        pygame.draw.ellipse(surf, body_color,
            (cx-22, my+28, 44, 38))

        surf.set_clip(None)

        # Head (above hole)
        head_top = my + 4
        pygame.draw.circle(surf, body_color, (cx, my+26), 24)
        # Cheeks
        pygame.draw.ellipse(surf, PINK, (cx-24, my+22, 14, 10))
        pygame.draw.ellipse(surf, PINK, (cx+10, my+22, 14, 10))
        # Snout
        pygame.draw.ellipse(surf, CREAM, (cx-10, my+22, 20, 14))
        pygame.draw.ellipse(surf, DKBROWN, (cx-5, my+24, 7, 5))
        pygame.draw.ellipse(surf, DKBROWN, (cx+0, my+24, 7, 5))
        # Mouth
        pygame.draw.arc(surf, DKBROWN,
            (cx-8, my+28, 16, 10), math.pi, 2*math.pi, 2)
        # Eyes
        if self.eyes_open or self.state == 'hit':
            pygame.draw.circle(surf, WHITE, (cx-9, my+16), 7)
            pygame.draw.circle(surf, WHITE, (cx+9, my+16), 7)
            if self.state != 'hit':
                pygame.draw.circle(surf, BLACK, (cx-8, my+17), 4)
                pygame.draw.circle(surf, BLACK, (cx+10, my+17), 4)
                pygame.draw.circle(surf, WHITE, (cx-7, my+16), 2)
                pygame.draw.circle(surf, WHITE, (cx+11, my+16), 2)
            else:
                # X eyes
                for ex, ey in [(cx-9, my+16), (cx+9, my+16)]:
                    pygame.draw.line(surf, RED, (ex-4,ey-4),(ex+4,ey+4),2)
                    pygame.draw.line(surf, RED, (ex+4,ey-4),(ex-4,ey+4),2)
        else:
            pygame.draw.line(surf, DKBROWN, (cx-14,my+16),(cx-4,my+16),2)
            pygame.draw.line(surf, DKBROWN, (cx+4, my+16),(cx+14,my+16),2)

        # Ears
        pygame.draw.ellipse(surf, body_color, (cx-28, my+4, 14, 18))
        pygame.draw.ellipse(surf, PINK,       (cx-26, my+7, 10, 12))
        pygame.draw.ellipse(surf, body_color, (cx+14, my+4, 14, 18))
        pygame.draw.ellipse(surf, PINK,       (cx+16, my+7, 10, 12))

        # Hat (golden / hard)
        if data['hat']:
            hc = GOLD if self.kind==GOLDEN else PURPLE
            dark_hc = (180,140,0) if self.kind==GOLDEN else (100,20,160)
            pygame.draw.rect(surf, hc,     (cx-14, my-4,  28, 18))
            pygame.draw.rect(surf, dark_hc,(cx-14, my-4,  28, 18), 2)
            pygame.draw.rect(surf, hc,     (cx-20, my+12, 40,  7))
            pygame.draw.rect(surf, dark_hc,(cx-20, my+12, 40,  7), 2)
            if self.kind == GOLDEN:
                pygame.draw.rect(surf, RED, (cx-10, my+1, 20, 5))

        # Bomb indicator
        if data['bomb']:
            # fuse
            pygame.draw.circle(surf, DKGREY, (cx, my+4), 12)
            pygame.draw.line(surf, ORANGE, (cx, my+4),(cx+8,my-8),2)
            pygame.draw.circle(surf, YELLOW, (cx+8,my-8), 3)
            t = pygame.font.SysFont("Courier",13,bold=True).render("💣",True,WHITE)
            surf.blit(t,(cx-8,my-4))

        # HP pips for hard mole
        if self.kind == HARD and self.hp > 1:
            pygame.draw.circle(surf, RED, (cx, my-8), 5)

        # Hole front (covers body bottom)
        pygame.draw.ellipse(surf, DKBROWN,
            (self.cx-self.rx, self.cy-self.ry, self.rx*2, self.ry*2))
        surf.set_clip(pygame.Rect(0, self.cy - self.ry + 6, WIDTH, HEIGHT))
        pygame.draw.ellipse(surf, DKGREEN,
            (self.cx-self.rx-2, self.cy-self.ry+2, (self.rx+2)*2, (self.ry+2)*2))
        pygame.draw.ellipse(surf, DKBROWN,
            (self.cx-self.rx, self.cy-self.ry, self.rx*2, self.ry*2))
        surf.set_clip(old_clip)

# ── Hammer cursor ──────────────────────────────────────────────────────────────
class Hammer:
    def __init__(self):
        self.angle = -30
        self.swing = False
        self.timer = 0

    def whack(self):
        self.swing = True
        self.timer = 12

    def update(self):
        if self.swing:
            self.timer -= 1
            self.angle = -30 + (12-self.timer)/12 * 80
            if self.timer <= 0:
                self.swing = False
                self.angle = -30

    def draw(self, surf, mx, my):
        ang = math.radians(self.angle)
        # handle
        hx = mx + math.cos(ang)*30
        hy = my + math.sin(ang)*30
        pygame.draw.line(surf, BROWN, (mx,my), (int(hx),int(hy)), 6)
        # head
        hcx = int(hx + math.cos(ang)*16)
        hcy = int(hy + math.sin(ang)*16)
        perp = ang + math.pi/2
        pts = [
            (hcx + math.cos(perp)*12, hcy + math.sin(perp)*12),
            (hcx - math.cos(perp)*12, hcy - math.sin(perp)*12),
            (hcx + math.cos(ang)*18 - math.cos(perp)*12,
             hcy + math.sin(ang)*18 - math.sin(perp)*12),
            (hcx + math.cos(ang)*18 + math.cos(perp)*12,
             hcy + math.sin(ang)*18 + math.sin(perp)*12),
        ]
        pygame.draw.polygon(surf, DKGREY, pts)
        pygame.draw.polygon(surf, GREY, pts, 2)

# ── Game ───────────────────────────────────────────────────────────────────────
class Game:
    GRID = [(150,240),(300,240),(450,240),
            (150,360),(300,360),(450,360),
            (150,480),(300,480),(450,480)]
    TIME_LIMIT  = 60
    LEVEL_EVERY = 1000

    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=RATE, size=-16, channels=2, buffer=512)
        pygame.mouse.set_visible(False)
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption("Whack-a-Mole")
        self.clock  = pygame.time.Clock()
        self.font_xl = pygame.font.SysFont("Courier",52,bold=True)
        self.font_lg = pygame.font.SysFont("Courier",36,bold=True)
        self.font_md = pygame.font.SysFont("Courier",24,bold=True)
        self.font_sm = pygame.font.SysFont("Courier",16)

        try:
            self.snd_whack   = snd_whack()
            self.snd_miss    = snd_miss()
            self.snd_appear  = snd_appear()
            self.snd_golden  = snd_golden()
            self.snd_bomb    = snd_bomb()
            self.snd_gameover= snd_gameover()
            self.snd_levelup = snd_levelup()
        except Exception:
            class _S:
                def play(self): pass
            dummy = _S()
            for a in ['snd_whack','snd_miss','snd_appear','snd_golden',
                      'snd_bomb','snd_gameover','snd_levelup']:
                setattr(self, a, dummy)

        self.holes = [Hole(cx,cy,i) for i,(cx,cy) in enumerate(self.GRID)]
        self.hammer = Hammer()
        self.hi = 0
        self.new_game()

    def new_game(self):
        self.score     = 0
        self.misses    = 0
        self.hits      = 0
        self.combo     = 0
        self.max_combo = 0
        self.level     = 1
        self.timer     = self.TIME_LIMIT * FPS
        self.spawn_cd  = 60
        self.particles = []
        self.floats    = []
        self.state     = 'playing'
        self.level_flash = 0
        for h in self.holes:
            h.state  = 'hidden'
            h.active = False
            h.offset = h.mole_h
        self.spawn_cd = 80

    def _level_up(self):
        self.level += 1
        self.level_flash = 90
        self.snd_levelup.play()
        for h in self.holes:
            cx,cy = h.cx, h.cy
            for _ in range(12):
                self.particles.append(StarParticle(cx,cy))

    def _spawn(self):
        empty = [h for h in self.holes if not h.active]
        if not empty: return
        h = random.choice(empty)
        lv = self.level
        # kind weights
        w = {NORMAL:60, GOLDEN:10, BOMB:10, SPEEDY:12, HARD:8}
        if lv >= 3: w[BOMB] = 15; w[GOLDEN] = 12
        if lv >= 5: w[HARD] = 15; w[SPEEDY] = 18
        kinds = list(w.keys())
        weights = [w[k] for k in kinds]
        kind = random.choices(kinds, weights)[0]
        up_time = max(45, 120 - lv*10)
        if kind == SPEEDY: up_time = max(30, up_time - 25)
        if kind == GOLDEN: up_time = max(50, up_time + 10)
        h.spawn(kind, up_time)
        if kind == GOLDEN: self.snd_golden.play()
        else: self.snd_appear.play()

    def _whack(self, mx, my):
        self.hammer.whack()
        hit_any = False
        for h in self.holes:
            if not h.active: continue
            if abs(mx-h.cx) < h.rx*1.1 and abs(my-(h.cy-h.ry+6)) < h.mole_h*0.85:
                if h.state in ('up','rising'):
                    if h.whack():
                        hit_any = True
                        data = MOLE_DATA[h.kind]
                        pts = data['pts']
                        if data['bomb']:
                            self.score = max(0, self.score+pts)
                            self.combo = 0
                            self.snd_bomb.play()
                            for _ in range(30):
                                self.particles.append(Particle(h.cx, h.cy-20, RED, 7, 45, 6))
                            self.floats.append(FloatingText(h.cx, h.cy-40, f"{pts}", RED, 30))
                        else:
                            self.combo += 1
                            self.max_combo = max(self.max_combo, self.combo)
                            mult = min(self.combo, 5)
                            total = pts * mult
                            self.score += total
                            self.hits  += 1
                            self.snd_whack.play()
                            col = MOLE_DATA[h.kind]['color']
                            for _ in range(16):
                                self.particles.append(Particle(h.cx, h.cy-20, col, 5, 38, 5))
                            if h.kind == GOLDEN:
                                for _ in range(10):
                                    self.particles.append(StarParticle(h.cx, h.cy-30))
                            label = f"+{total}" + ("  x"+str(mult) if mult>1 else "")
                            self.floats.append(FloatingText(h.cx, h.cy-50, label,
                                               GOLD if mult>1 else YELLOW, 28))
                            if self.score // self.LEVEL_EVERY > (self.score-total)//self.LEVEL_EVERY:
                                self._level_up()
                        self.hi = max(self.hi, self.score)
        if not hit_any:
            self.misses += 1
            self.combo   = 0
            self.snd_miss.play()
            self.floats.append(FloatingText(mx, my-20, "MISS", GREY, 20))

    def update(self):
        if self.state != 'playing': return
        self.timer -= 1
        if self.timer <= 0:
            self.state = 'gameover'
            self.hi = max(self.hi, self.score)
            self.snd_gameover.play()
            return

        for h in self.holes: h.update()
        self.hammer.update()

        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        for f in self.floats: f.update()
        self.floats = [f for f in self.floats if f.life > 0]

        self.spawn_cd -= 1
        if self.spawn_cd <= 0:
            n = 1 if self.level < 3 else (2 if self.level < 6 else 3)
            for _ in range(n): self._spawn()
            base = max(30, 80 - self.level*8)
            self.spawn_cd = base + random.randint(-10,10)

        if self.level_flash > 0: self.level_flash -= 1

    def draw(self):
        # Sky gradient
        for y in range(HEIGHT):
            t = y/HEIGHT
            r = int(100*(1-t)+30*t)
            g = int(180*(1-t)+120*t)
            b = int(255*(1-t)+80*t)
            pygame.draw.line(self.screen,(r,g,b),(0,y),(WIDTH,y))

        # Grass
        pygame.draw.rect(self.screen, GRASS, (0, 540, WIDTH, HEIGHT-540))
        pygame.draw.rect(self.screen, DKGREEN,(0,535,WIDTH,10))

        # Clouds
        for cx,cy in [(100,80),(300,50),(500,90),(200,130)]:
            for ox,oy,r in [(0,0,28),(25,-10,22),(-25,-8,20),(40,5,18),(-38,5,16)]:
                pygame.draw.circle(self.screen,(230,240,255),(cx+ox,cy+oy),r)

        # Holes
        for h in self.holes: h.draw(self.screen)

        # Particles
        for p in self.particles: p.draw(self.screen)
        for f in self.floats: f.draw(self.screen)

        # HUD
        pygame.draw.rect(self.screen, (0,0,0,180), (0,0,WIDTH,55))
        pygame.draw.line(self.screen, GREEN, (0,55),(WIDTH,55),2)

        sc = self.font_md.render(f"Score: {self.score}", True, YELLOW)
        self.screen.blit(sc,(10,12))

        hi = self.font_sm.render(f"HI:{self.hi}", True, GOLD)
        self.screen.blit(hi,(10,36))

        secs = math.ceil(self.timer/FPS)
        tc = RED if secs <= 10 else WHITE
        tm = self.font_md.render(f"⏱ {secs}s", True, tc)
        self.screen.blit(tm,(WIDTH//2 - tm.get_width()//2, 14))

        lv = self.font_sm.render(f"LV {self.level}", True, CYAN)
        self.screen.blit(lv,(WIDTH - lv.get_width()-10, 8))

        if self.combo > 1:
            ct = self.font_sm.render(f"x{min(self.combo,5)} COMBO!", True, ORANGE)
            self.screen.blit(ct,(WIDTH - ct.get_width()-10, 30))

        # Timer bar
        bar_w = int((self.timer/(self.TIME_LIMIT*FPS))*WIDTH)
        bc = RED if secs<=10 else (ORANGE if secs<=20 else GREEN)
        pygame.draw.rect(self.screen, (30,30,30),(0,52,WIDTH,5))
        pygame.draw.rect(self.screen, bc,(0,52,bar_w,5))

        # Hammer
        mx,my = pygame.mouse.get_pos()
        self.hammer.draw(self.screen, mx, my)

        # Level flash
        if self.level_flash > 0:
            a = self.level_flash/90
            s = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
            s.fill((0,0,0,int(120*a)))
            self.screen.blit(s,(0,0))
            t1 = self.font_xl.render(f"LEVEL {self.level}!", True, GOLD)
            t2 = self.font_sm.render("Speed increased!", True, WHITE)
            self.screen.blit(t1,(WIDTH//2-t1.get_width()//2, HEIGHT//2-40))
            self.screen.blit(t2,(WIDTH//2-t2.get_width()//2, HEIGHT//2+30))

        if self.state == 'gameover':
            s = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
            s.fill((0,0,0,170))
            self.screen.blit(s,(0,0))
            t = self.font_xl.render("TIME'S UP!", True, RED)
            self.screen.blit(t,(WIDTH//2-t.get_width()//2, HEIGHT//2-100))
            sc2 = self.font_lg.render(f"Score: {self.score}", True, YELLOW)
            self.screen.blit(sc2,(WIDTH//2-sc2.get_width()//2, HEIGHT//2-20))
            hi2 = self.font_md.render(f"Hi-Score: {self.hi}", True, GOLD)
            self.screen.blit(hi2,(WIDTH//2-hi2.get_width()//2, HEIGHT//2+40))
            stats = self.font_sm.render(
                f"Hits: {self.hits}   Misses: {self.misses}   Best Combo: x{self.max_combo}",
                True, WHITE)
            self.screen.blit(stats,(WIDTH//2-stats.get_width()//2, HEIGHT//2+90))
            r = self.font_md.render("R — Play Again   Q — Quit", True, CYAN)
            self.screen.blit(r,(WIDTH//2-r.get_width()//2, HEIGHT//2+140))

        if self.state == 'title':
            self._draw_title()

        pygame.display.flip()

    def _draw_title(self):
        s = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        s.fill((0,0,0,160))
        self.screen.blit(s,(0,0))
        t1 = self.font_xl.render("WHACK-A-MOLE",True,GREEN)
        self.screen.blit(t1,(WIDTH//2-t1.get_width()//2,160))
        t2 = self.font_md.render("Click to whack moles!",True,WHITE)
        self.screen.blit(t2,(WIDTH//2-t2.get_width()//2,260))
        tips=[
            (BROWN,  "Normal = +10 pts"),
            (GOLD,   "Golden = +50 pts"),
            (ORANGE, "Speedy = +20 pts (fast!)"),
            (PURPLE, "Hard   = +30 pts (2 hits)"),
            (RED,    "Bomb   = -30 pts (avoid!)"),
        ]
        for i,(c,txt) in enumerate(tips):
            t=self.font_sm.render(txt,True,c)
            self.screen.blit(t,(WIDTH//2-t.get_width()//2, 320+i*28))
        sp=self.font_md.render("CLICK TO START",True,YELLOW)
        if (pygame.time.get_ticks()//500)%2==0:
            self.screen.blit(sp,(WIDTH//2-sp.get_width()//2,490))

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q: pygame.quit(); sys.exit()
                if e.key == pygame.K_r:
                    self.new_game()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.state == 'title':
                    self.new_game()
                elif self.state == 'playing':
                    self._whack(*e.pos)
                elif self.state == 'gameover':
                    self.new_game()

    def run(self):
        self.state = 'title'
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()
