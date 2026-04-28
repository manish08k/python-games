"""
Pinball — Python + Pygame
Run: python pinball.py
Requires: pip install pygame numpy
"""

import pygame
import sys
import math
import random
import numpy as np

WIDTH, HEIGHT = 500, 750
FPS = 60

BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
CYAN    = (0,   220, 255)
YELLOW  = (255, 230, 0)
RED     = (255, 50,  50)
ORANGE  = (255, 140, 0)
GREEN   = (0,   220, 80)
MAGENTA = (220, 0,   220)
BLUE    = (30,  80,  255)
GREY    = (80,  80,  80)
DKGREY  = (25,  25,  40)
PINK    = (255, 100, 180)
LBLUE   = (100, 180, 255)

RATE = 22050

def _buf(arr, vol=0.6):
    a = np.clip(arr * vol * 32767, -32767, 32767).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack([a, a]))

def snd_bump(freq=440, dur=0.08):
    t = np.linspace(0, dur, int(RATE*dur))
    s = np.sin(2*np.pi*freq*t) * np.exp(-10*t/dur)
    return _buf(s)

def snd_flipper_snd():
    t = np.linspace(0, 0.06, int(RATE*0.06))
    s = np.sign(np.sin(2*np.pi*180*t)) * np.linspace(0.5,0,len(t))
    return _buf(s)

def snd_drain_snd():
    t = np.linspace(0, 0.4, int(RATE*0.4))
    f = np.linspace(300, 60, len(t))
    s = np.sin(2*np.pi*f*t) * np.exp(-4*t/0.4)
    return _buf(s)

def snd_launch_snd():
    t = np.linspace(0, 0.12, int(RATE*0.12))
    f = np.linspace(200, 800, len(t))
    s = np.sin(2*np.pi*f*t) * np.exp(-5*t/0.12)
    return _buf(s)

def snd_extra_snd():
    t = np.linspace(0, 0.3, int(RATE*0.3))
    f = np.linspace(400, 900, len(t))
    s = np.sin(2*np.pi*f*t) * np.linspace(0.6,0,len(t))
    return _buf(s)

# ── Math ───────────────────────────────────────────────────────────────────────
def dot(a, b): return a[0]*b[0] + a[1]*b[1]
def norm(v): m=math.hypot(*v); return (v[0]/m,v[1]/m) if m else (0,0)
def reflect(vel, n):
    d = 2*dot(vel,n)
    return (vel[0]-d*n[0], vel[1]-d*n[1])

def closest_point_on_segment(px, py, ax, ay, bx, by):
    dx, dy = bx-ax, by-ay
    if dx==0 and dy==0: return ax, ay
    t = max(0, min(1, ((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy)))
    return ax+t*dx, ay+t*dy

def circle_seg_collide(bx, by, br, ax, ay, segbx, segby):
    cx, cy = closest_point_on_segment(bx, by, ax, ay, segbx, segby)
    dx, dy = bx-cx, by-cy
    d = math.hypot(dx, dy)
    if d < br and d > 0:
        nx, ny = dx/d, dy/d
        return True, cx, cy, nx, ny, d
    return False, 0, 0, 0, 0, 0

# ── Bumper ─────────────────────────────────────────────────────────────────────
class Bumper:
    def __init__(self, x, y, r=20, pts=100, color=CYAN):
        self.x, self.y = x, y
        self.r = r
        self.pts = pts
        self.color = color
        self.flash = 0

    def check(self, ball):
        dx, dy = ball.x - self.x, ball.y - self.y
        d = math.hypot(dx, dy)
        if d < self.r + ball.r and d > 0:
            nx, ny = dx/d, dy/d
            speed = math.hypot(ball.vx, ball.vy)
            bounce = max(speed * 1.4, 8.0)
            ball.vx = nx * bounce
            ball.vy = ny * bounce
            overlap = (self.r + ball.r) - d
            ball.x += nx * overlap
            ball.y += ny * overlap
            self.flash = 12
            return True
        return False

    def draw(self, surf):
        f = self.flash / 12.0
        r, g, b = self.color
        fc = (min(255,int(r+f*(255-r))), min(255,int(g+f*(255-g))), min(255,int(b+f*(255-b))))
        pygame.draw.circle(surf, fc,    (int(self.x),int(self.y)), self.r)
        pygame.draw.circle(surf, WHITE, (int(self.x),int(self.y)), self.r, 2)
        pts_txt = pygame.font.SysFont("Courier",11,bold=True).render(str(self.pts),True,BLACK)
        surf.blit(pts_txt,(int(self.x)-pts_txt.get_width()//2, int(self.y)-pts_txt.get_height()//2))
        if self.flash > 0: self.flash -= 1

# ── Slingshot ──────────────────────────────────────────────────────────────────
class Slingshot:
    def __init__(self, pts, pts_val=50, color=ORANGE):
        self.pts = pts   # list of (x,y) polygon
        self.pts_val = pts_val
        self.color = color
        self.flash = 0
        self.segments = [(pts[i], pts[(i+1)%len(pts)]) for i in range(len(pts))]

    def check(self, ball):
        hit = False
        for (ax,ay),(bx,by) in self.segments:
            ok, cx, cy, nx, ny, d = circle_seg_collide(ball.x, ball.y, ball.r, ax, ay, bx, by)
            if ok:
                speed = math.hypot(ball.vx, ball.vy)
                rv = reflect((ball.vx, ball.vy), (nx, ny))
                boost = max(speed*1.3, 7.0)
                ln = math.hypot(*rv)
                ball.vx = rv[0]/ln*boost if ln else nx*boost
                ball.vy = rv[1]/ln*boost if ln else ny*boost
                ball.x += nx * (ball.r - d + 1)
                ball.y += ny * (ball.r - d + 1)
                self.flash = 10
                hit = True
        return hit

    def draw(self, surf):
        f = self.flash / 10.0
        r, g, b = self.color
        fc = (min(255,int(r*0.5+f*r)), min(255,int(g*0.5+f*g)), min(255,int(b*0.5+f*b)))
        pygame.draw.polygon(surf, fc, self.pts)
        pygame.draw.polygon(surf, WHITE, self.pts, 2)
        if self.flash > 0: self.flash -= 1

# ── Target ─────────────────────────────────────────────────────────────────────
class Target:
    def __init__(self, x, y, w, h, pts=200, color=MAGENTA):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.pts = pts
        self.color = color
        self.hit = False
        self.flash = 0

    def reset(self): self.hit = False

    def check(self, ball):
        if self.hit: return False
        r = pygame.Rect(self.x-self.w//2, self.y-self.h//2, self.w, self.h)
        br= pygame.Rect(int(ball.x-ball.r), int(ball.y-ball.r), ball.r*2, ball.r*2)
        if r.colliderect(br):
            self.hit = True
            self.flash = 20
            ball.vy = -abs(ball.vy) - 2
            return True
        return False

    def draw(self, surf):
        if self.hit:
            pygame.draw.rect(surf, DKGREY, (self.x-self.w//2, self.y-self.h//2, self.w, self.h))
            pygame.draw.rect(surf, GREY,   (self.x-self.w//2, self.y-self.h//2, self.w, self.h), 2)
        else:
            f = self.flash/20
            r,g,b = self.color
            fc=(min(255,int(r+f*100)),min(255,int(g+f*100)),min(255,int(b+f*100)))
            pygame.draw.rect(surf, fc,    (self.x-self.w//2, self.y-self.h//2, self.w, self.h))
            pygame.draw.rect(surf, WHITE, (self.x-self.w//2, self.y-self.h//2, self.w, self.h),2)
        if self.flash > 0: self.flash -= 1

# ── Flipper ────────────────────────────────────────────────────────────────────
class Flipper:
    LEN   = 68
    W     = 8
    REST_L =  30   # degrees (up from horizontal)
    REST_R = 150
    ACT_L  = -20
    ACT_R  = 200
    SPEED  = 18

    def __init__(self, x, y, side):
        self.x, self.y = x, y
        self.side = side   # 'left' or 'right'
        self.angle = self.REST_L if side=='left' else self.REST_R
        self.active = False

    @property
    def rest(self): return self.REST_L if self.side=='left' else self.REST_R
    @property
    def act(self):  return self.ACT_L  if self.side=='left' else self.ACT_R

    def update(self, pressed):
        target = self.act if pressed else self.rest
        diff   = target - self.angle
        step   = self.SPEED * (1 if diff>0 else -1)
        if abs(diff) < self.SPEED:
            self.angle = target
        else:
            self.angle += step
        self.active = pressed

    def tip(self):
        r = math.radians(self.angle)
        return (self.x + math.cos(r)*self.LEN, self.y + math.sin(r)*self.LEN)

    def check(self, ball):
        tx, ty = self.tip()
        ok, cx, cy, nx, ny, d = circle_seg_collide(ball.x, ball.y, ball.r, self.x, self.y, tx, ty)
        if ok:
            flip_spd = 6.0 if self.active else 1.0
            rv = reflect((ball.vx, ball.vy), (nx, ny))
            boost = max(math.hypot(*rv), 4.0)
            if self.active:
                boost = max(boost, 9.0) + flip_spd
            ball.vx = rv[0]/math.hypot(*rv)*boost if math.hypot(*rv) else nx*boost
            ball.vy = rv[1]/math.hypot(*rv)*boost if math.hypot(*rv) else ny*boost
            ball.x += nx*(ball.r-d+1)
            ball.y += ny*(ball.r-d+1)
            return True
        return False

    def draw(self, surf):
        tx, ty = self.tip()
        pts = []
        perp_ang = math.radians(self.angle + 90)
        px, py = math.cos(perp_ang)*self.W, math.sin(perp_ang)*self.W
        pts = [
            (self.x+px*0.6, self.y+py*0.6),
            (self.x-px*0.6, self.y-py*0.6),
            (tx-px*0.3,     ty-py*0.3),
            (tx+px*0.3,     ty+py*0.3),
        ]
        color = YELLOW if self.active else (180,160,0)
        pygame.draw.polygon(surf, color, pts)
        pygame.draw.polygon(surf, WHITE, pts, 2)
        pygame.draw.circle(surf, WHITE, (int(self.x),int(self.y)), 6)

# ── Wall segments ──────────────────────────────────────────────────────────────
class Wall:
    def __init__(self, ax, ay, bx, by, color=BLUE):
        self.ax, self.ay = ax, ay
        self.bx, self.by = bx, by
        self.color = color

    def check(self, ball):
        ok, cx, cy, nx, ny, d = circle_seg_collide(ball.x, ball.y, ball.r, self.ax, self.ay, self.bx, self.by)
        if ok:
            rv = reflect((ball.vx, ball.vy), (nx, ny))
            speed = math.hypot(*rv)
            ball.vx, ball.vy = rv[0], rv[1]
            ball.x += nx*(ball.r-d+1)
            ball.y += ny*(ball.r-d+1)
            return True
        return False

    def draw(self, surf):
        pygame.draw.line(surf, self.color, (int(self.ax),int(self.ay)), (int(self.bx),int(self.by)), 3)

# ── Ball ───────────────────────────────────────────────────────────────────────
class Ball:
    r    = 10
    GRAV = 0.28

    def __init__(self):
        self.reset()

    def reset(self):
        self.x  = WIDTH - 28
        self.y  = HEIGHT - 120
        self.vx = 0.0
        self.vy = 0.0
        self.launched = False
        self.trail = []

    def launch(self, power):
        self.vy = -power
        self.vx = random.uniform(-0.5, 0.5)
        self.launched = True

    def update(self):
        if not self.launched: return
        self.vy += self.GRAV
        self.x  += self.vx
        self.y  += self.vy
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 14: self.trail.pop(0)
        # side walls
        if self.x - self.r < 22:
            self.x = 22 + self.r
            self.vx = abs(self.vx) * 0.85
        if self.x + self.r > WIDTH - 22:
            self.x = WIDTH - 22 - self.r
            self.vx = -abs(self.vx) * 0.85
        # top
        if self.y - self.r < 40:
            self.y = 40 + self.r
            self.vy = abs(self.vy) * 0.8

    def draw(self, surf):
        for i, (tx,ty) in enumerate(self.trail):
            a = (i+1)/len(self.trail)
            c = (int(200*a), int(200*a), 255)
            pygame.draw.circle(surf, c, (tx,ty), max(1, int(self.r*a*0.6)))
        pygame.draw.circle(surf, WHITE, (int(self.x),int(self.y)), self.r)
        pygame.draw.circle(surf, LBLUE, (int(self.x)-3,int(self.y)-3), self.r//3)

# ── Particle ───────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color):
        a = random.uniform(0,360)
        s = random.uniform(1,5)
        r = math.radians(a)
        self.x, self.y   = x, y
        self.vx = math.cos(r)*s
        self.vy = math.sin(r)*s
        self.life = self.ml = random.randint(20,45)
        self.color = color
        self.sz = random.uniform(2,5)

    def update(self):
        self.x  += self.vx; self.y += self.vy
        self.vx *= 0.93;    self.vy *= 0.93
        self.life -= 1

    def draw(self, surf):
        a = self.life/self.ml
        r,g,b = self.color
        c = (int(r*a),int(g*a),int(b*a))
        pygame.draw.circle(surf, c, (int(self.x),int(self.y)), max(1,int(self.sz*a)))

# ── Plunger ────────────────────────────────────────────────────────────────────
class Plunger:
    MAX_POWER = 22.0
    MIN_POWER = 8.0

    def __init__(self):
        self.power = 0.0
        self.charging = False

    def update(self, holding):
        if holding:
            self.charging = True
            self.power = min(self.power + 0.6, self.MAX_POWER)
        elif self.charging:
            released = max(self.power, self.MIN_POWER)
            self.power = 0.0
            self.charging = False
            return released
        return None

    def draw(self, surf, ball):
        if not ball.launched:
            bx, by = int(ball.x), int(ball.y)
            ph = int(self.power * 2.5)
            pygame.draw.rect(surf, ORANGE, (WIDTH-38, by+ball.r, 16, ph))
            pygame.draw.rect(surf, YELLOW, (WIDTH-38, by+ball.r, 16, ph), 2)
            # power bar
            for i in range(int(self.power)):
                c = (min(255,i*12), max(0,255-i*12), 0)
                pygame.draw.rect(surf, c, (WIDTH-14, HEIGHT-100-i*5, 10, 4))

# ── Score popup ────────────────────────────────────────────────────────────────
class ScorePopup:
    def __init__(self, x, y, pts, color=YELLOW):
        self.x, self.y = x, y
        self.pts = pts
        self.color = color
        self.life = 45

    def update(self): self.y -= 0.8; self.life -= 1

    def draw(self, surf, font):
        a = self.life/45
        r,g,b = self.color
        c = (int(r*a),int(g*a),int(b*a))
        t = font.render(f"+{self.pts}", True, c)
        surf.blit(t, (int(self.x)-t.get_width()//2, int(self.y)))

# ── Main Game ──────────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=RATE, size=-16, channels=2, buffer=512)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pinball")
        self.clock  = pygame.time.Clock()
        self.font_lg = pygame.font.SysFont("Courier", 36, bold=True)
        self.font_md = pygame.font.SysFont("Courier", 22, bold=True)
        self.font_sm = pygame.font.SysFont("Courier", 14)
        self.font_xs = pygame.font.SysFont("Courier", 12)

        try:
            self.snd_bump    = [snd_bump(440,0.08), snd_bump(550,0.08), snd_bump(660,0.08)]
            self.snd_sling   = snd_bump(300, 0.1)
            self.snd_flipper = snd_flipper_snd()
            self.snd_drain   = snd_drain_snd()
            self.snd_launch  = snd_launch_snd()
            self.snd_extra   = snd_extra_snd()
            self.snd_target  = snd_bump(800, 0.06)
        except Exception:
            class _S:
                def play(self): pass
            dummy = _S()
            for a in ['snd_bump','snd_sling','snd_flipper','snd_drain','snd_launch','snd_extra','snd_target']:
                setattr(self, a, dummy if a!='snd_bump' else [dummy,dummy,dummy])

        self.hi = 0
        self._build_table()
        self.new_game()

    def _build_table(self):
        # Outer walls
        self.walls = [
            Wall(22, 40, 22, HEIGHT-80),
            Wall(WIDTH-22, 40, WIDTH-22, HEIGHT-160),
            # top arc approximated as segments
            Wall(22, 40, WIDTH//2-10, 30),
            Wall(WIDTH//2+10, 30, WIDTH-22, 40),
            # inlane guides
            Wall(22, HEIGHT-200, 80, HEIGHT-130),
            Wall(WIDTH-22, HEIGHT-200, WIDTH-80, HEIGHT-130),
            # drain channel right
            Wall(WIDTH-22, HEIGHT-160, WIDTH-22, HEIGHT-50),
        ]
        # Slingshots
        self.slings = [
            Slingshot([(80,490),(130,460),(130,530)], 50, ORANGE),
            Slingshot([(WIDTH-80,490),(WIDTH-130,460),(WIDTH-130,530)], 50, ORANGE),
        ]
        # Bumpers
        self.bumpers = [
            Bumper(180, 230, 22, 100, CYAN),
            Bumper(280, 200, 22, 100, RED),
            Bumper(350, 260, 22, 100, GREEN),
            Bumper(230, 310, 22, 100, MAGENTA),
            Bumper(310, 160, 18,  80, YELLOW),
        ]
        # Targets (top row)
        self.targets = [
            Target(120, 120, 30, 14, 200, PINK),
            Target(175, 110, 30, 14, 200, PINK),
            Target(230, 105, 30, 14, 200, PINK),
            Target(285, 110, 30, 14, 200, PINK),
            Target(340, 120, 30, 14, 200, PINK),
        ]
        # Flippers
        self.fl = Flipper(130, HEIGHT-80, 'left')
        self.fr = Flipper(WIDTH-130, HEIGHT-80, 'right')

        # Lane guide walls (angled inlanes)
        self.walls += [
            Wall(22, HEIGHT-130, 90, HEIGHT-80),
            Wall(WIDTH-22, HEIGHT-130, WIDTH-90, HEIGHT-80),
        ]

    def new_game(self):
        self.score    = 0
        self.lives    = 3
        self.ball     = Ball()
        self.plunger  = Plunger()
        self.particles= []
        self.popups   = []
        self.state    = 'plunging'
        self.drain_timer = 0
        self.combo    = 0
        self.combo_timer = 0
        self.targets_hit = 0
        self.bonus_lit  = False
        self.tick = 0
        for t in self.targets: t.reset()

    def _add_score(self, pts, x, y, color=YELLOW):
        mult = 1
        if self.combo > 1: mult = min(self.combo, 5)
        total = pts * mult
        self.score += total
        self.hi = max(self.hi, self.score)
        self.combo += 1
        self.combo_timer = 120
        self.popups.append(ScorePopup(x, y, total, color))
        for _ in range(8):
            self.particles.append(Particle(x, y, color))

    def update(self):
        self.tick += 1
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

        keys = pygame.key.get_pressed()

        # Plunger
        if self.state == 'plunging':
            power = self.plunger.update(keys[pygame.K_DOWN] or keys[pygame.K_s])
            if power:
                self.ball.launch(power)
                self.snd_launch.play()
                self.state = 'playing'
            return

        if self.state != 'playing': return

        # Flippers
        lp = keys[pygame.K_z] or keys[pygame.K_LSHIFT] or keys[pygame.K_LEFT]
        rp = keys[pygame.K_x] or keys[pygame.K_RSHIFT] or keys[pygame.K_RIGHT] or keys[pygame.K_SLASH]
        prev_la = self.fl.active
        prev_ra = self.fr.active
        self.fl.update(lp)
        self.fr.update(rp)
        if self.fl.active != prev_la or self.fr.active != prev_ra:
            self.snd_flipper.play()

        self.ball.update()

        # Wall collisions
        for w in self.walls:
            w.check(self.ball)

        # Flipper collisions
        self.fl.check(self.ball)
        self.fr.check(self.ball)

        # Bumpers
        for b in self.bumpers:
            if b.check(self.ball):
                random.choice(self.snd_bump).play()
                self._add_score(b.pts, b.x, b.y, b.color)

        # Slingshots
        for s in self.slings:
            if s.check(self.ball):
                self.snd_sling.play()
                self._add_score(s.pts_val, int(self.ball.x), int(self.ball.y), ORANGE)

        # Targets
        all_hit_before = all(t.hit for t in self.targets)
        for t in self.targets:
            if t.check(self.ball):
                self.snd_target.play()
                self._add_score(t.pts, t.x, t.y, PINK)
                self.targets_hit += 1
        all_hit_now = all(t.hit for t in self.targets)
        if all_hit_now and not all_hit_before:
            self._add_score(2000, WIDTH//2, 300, YELLOW)
            self.snd_extra.play()
            for t in self.targets: t.reset()

        # Particles / popups
        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.popups: p.update()
        self.popups = [p for p in self.popups if p.life > 0]

        # Drain detection
        if self.ball.y > HEIGHT + 20:
            self.snd_drain.play()
            self.lives -= 1
            for _ in range(25):
                self.particles.append(Particle(self.ball.x, HEIGHT-40, RED))
            if self.lives <= 0:
                self.state = 'game_over'
                self.hi = max(self.hi, self.score)
            else:
                self.state = 'plunging'
                self.ball = Ball()
                self.plunger = Plunger()

    def draw(self):
        self.screen.fill(DKGREY)

        # Table background glow
        pygame.draw.rect(self.screen, (15,15,30), (22, 40, WIDTH-44, HEIGHT-120))

        # Decorative lane lines
        for y in range(60, HEIGHT-100, 60):
            pygame.draw.line(self.screen, (20,20,45), (22, y), (WIDTH-22, y), 1)

        # Objects
        for w in self.walls: w.draw(self.screen)
        for s in self.slings: s.draw(self.screen)
        for b in self.bumpers: b.draw(self.screen)
        for t in self.targets: t.draw(self.screen)

        for p in self.particles: p.draw(self.screen)
        self.ball.draw(self.screen)
        self.fl.draw(self.screen)
        self.fr.draw(self.screen)

        if self.state == 'plunging':
            self.plunger.draw(self.screen, self.ball)

        for p in self.popups: p.draw(self.screen, self.font_xs)

        # Side rail
        pygame.draw.rect(self.screen, (10,10,25), (WIDTH-22, 40, 22, HEIGHT-200))
        pygame.draw.line(self.screen, BLUE, (WIDTH-22,40),(WIDTH-22,HEIGHT-160),3)

        # HUD background
        pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, 38))
        pygame.draw.line(self.screen, CYAN, (0,38),(WIDTH,38),2)

        sc = self.font_md.render(f"{self.score:08d}", True, YELLOW)
        self.screen.blit(sc, (10, 8))
        hi = self.font_sm.render(f"HI {self.hi:08d}", True, GREY)
        self.screen.blit(hi, (WIDTH//2 - hi.get_width()//2, 12))

        # Lives
        for i in range(self.lives):
            pygame.draw.circle(self.screen, WHITE, (WIDTH-20-i*18, 20), 7)
            pygame.draw.circle(self.screen, LBLUE, (WIDTH-22-i*18, 18), 3)

        # Combo
        if self.combo > 1 and self.combo_timer > 0:
            ct = self.font_sm.render(f"x{self.combo} COMBO!", True, ORANGE)
            self.screen.blit(ct, (10, HEIGHT-18))

        # Bottom drain zone indicator
        pygame.draw.rect(self.screen, (40,0,0), (22, HEIGHT-40, WIDTH-44, 40))
        pygame.draw.line(self.screen, RED, (22,HEIGHT-40),(WIDTH-22,HEIGHT-40),2)

        if self.state == 'plunging':
            t = self.font_sm.render("HOLD ↓  RELEASE to launch", True, CYAN)
            self.screen.blit(t, (WIDTH//2-t.get_width()//2, HEIGHT-62))
        if self.state == 'game_over':
            s = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
            s.fill((0,0,0,160))
            self.screen.blit(s,(0,0))
            g = self.font_lg.render("GAME OVER", True, RED)
            self.screen.blit(g,(WIDTH//2-g.get_width()//2, HEIGHT//2-50))
            sc2 = self.font_md.render(f"Score: {self.score}", True, YELLOW)
            self.screen.blit(sc2,(WIDTH//2-sc2.get_width()//2, HEIGHT//2+10))
            r = self.font_sm.render("R — Restart   Q — Quit", True, WHITE)
            self.screen.blit(r,(WIDTH//2-r.get_width()//2, HEIGHT//2+55))

        pygame.display.flip()

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q: pygame.quit(); sys.exit()
                if e.key == pygame.K_r: self.new_game()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()
