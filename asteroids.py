"""
Asteroids — Python + Pygame
Run: python asteroids.py
Requires: pip install pygame numpy
"""

import pygame 
import sys
import math
import random
import numpy as np

# ── Constants ──────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 900, 700
FPS           = 60
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
CYAN   = (0,   220, 255)
YELLOW = (255, 230, 0)
RED    = (255, 60,  60)
ORANGE = (255, 140, 0)
GREEN  = (60,  255, 120)
GREY   = (120, 120, 120)
DKGREY = (40,  40,  40)

# ── Math helpers ───────────────────────────────────────────────────────────────
def wrap(x, y):
    return x % WIDTH, y % HEIGHT

def angle_to_vec(deg):
    r = math.radians(deg)
    return math.cos(r), -math.sin(r)

def dist(ax, ay, bx, by):
    return math.hypot(ax - bx, ay - by)

def poly_points(cx, cy, angle, shape):
    r = math.radians(angle)
    pts = []
    for (px, py) in shape:
        rx = px * math.cos(r) - py * math.sin(r)
        ry = px * math.sin(r) + py * math.cos(r)
        pts.append((cx + rx, cy + ry))
    return pts

# ── Sound synthesis ────────────────────────────────────────────────────────────
RATE = 22050

def _buf(arr):
    a = (arr * 32767).astype(np.int16)
    s = np.column_stack([a, a])
    return pygame.sndarray.make_sound(s)

def make_shoot_snd():
    t = np.linspace(0, 0.12, int(RATE * 0.12))
    f = np.linspace(900, 200, len(t))
    s = np.sin(2 * np.pi * f * t) * np.linspace(0.5, 0, len(t))
    return _buf(s)

def make_explode_snd(dur=0.35, freq=80):
    t = np.linspace(0, dur, int(RATE * dur))
    noise = np.random.uniform(-1, 1, len(t))
    env   = np.exp(-6 * t / dur)
    tone  = np.sin(2 * np.pi * freq * t) * 0.4
    return _buf((noise * 0.6 + tone) * env * 0.7)

def make_thrust_snd():
    t = np.linspace(0, 0.08, int(RATE * 0.08))
    noise = np.random.uniform(-1, 1, len(t))
    env   = np.linspace(0.3, 0, len(t))
    return _buf(noise * env)

def make_beat_snd(freq):
    t = np.linspace(0, 0.06, int(RATE * 0.06))
    s = np.sign(np.sin(2 * np.pi * freq * t)) * np.linspace(0.4, 0, len(t))
    return _buf(s)

def make_extra_life_snd():
    t = np.linspace(0, 0.3, int(RATE * 0.3))
    f = np.linspace(400, 800, len(t))
    s = np.sin(2 * np.pi * f * t) * np.linspace(0.5, 0, len(t))
    return _buf(s)

# ── Particle ───────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, vx, vy, life, color=WHITE, size=2):
        self.x, self.y   = x, y
        self.vx, self.vy = vx, vy
        self.life = self.max_life = life
        self.color = color
        self.size  = size

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vx *= 0.97
        self.vy *= 0.97
        self.x, self.y = wrap(self.x, self.y)
        self.life -= 1

    def draw(self, surf):
        alpha = self.life / self.max_life
        r, g, b = self.color
        c = (int(r*alpha), int(g*alpha), int(b*alpha))
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), max(1, int(self.size * alpha)))

def explode(x, y, n=22, color=ORANGE, speed=3.0):
    parts = []
    for _ in range(n):
        a = random.uniform(0, 360)
        s = random.uniform(0.3, speed)
        vx, vy = angle_to_vec(a)
        life   = random.randint(25, 55)
        sz     = random.uniform(1, 3)
        parts.append(Particle(x, y, vx*s, vy*s, life, color, sz))
    return parts

# ── Bullet ─────────────────────────────────────────────────────────────────────
class Bullet:
    SPEED  = 9.5
    LIFE   = 55

    def __init__(self, x, y, angle):
        vx, vy = angle_to_vec(angle)
        self.x  = x + vx * 18
        self.y  = y + vy * 18
        self.vx = vx * self.SPEED
        self.vy = vy * self.SPEED
        self.life = self.LIFE
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.x, self.y = wrap(self.x, self.y)
        self.life -= 1
        if self.life <= 0:
            self.alive = False

    def draw(self, surf):
        alpha = min(255, self.life * 8)
        color = (alpha, alpha, 255)
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), 3)
        pygame.draw.circle(surf, WHITE,  (int(self.x), int(self.y)), 2)

# ── Asteroid ───────────────────────────────────────────────────────────────────
ASTEROID_SHAPES = [
    [(-1.0, 0.0),(-0.7,-0.7),(0.0,-1.0),(0.7,-0.7),(1.0, 0.0),(0.7, 0.7),(0.0, 1.0),(-0.7, 0.7)],
    [(-0.9, 0.2),(-0.6,-0.8),(0.1,-1.0),(0.8,-0.6),(1.0, 0.1),(0.6, 0.9),(-0.2, 1.0),(-0.8, 0.5)],
    [(-1.0, 0.3),(-0.5,-0.9),(0.3,-1.0),(0.9,-0.5),(1.0, 0.4),(0.4, 0.9),(-0.3, 1.0),(-0.8, 0.4)],
    [(-0.8, 0.0),(-0.9,-0.5),(-0.3,-1.0),(0.5,-0.9),(1.0,-0.2),(0.8, 0.6),(0.1, 1.0),(-0.6, 0.8)],
]

SIZES = {
    'large':  (52, 1, 20, GREY),
    'medium': (30, 2, 50, GREY),
    'small':  (14, 3, 100, WHITE),
}

class Asteroid:
    def __init__(self, x, y, size='large', angle=None, speed=None):
        self.x, self.y = x, y
        self.size_name = size
        self.radius, self.tier, self.pts, self.color = SIZES[size]
        angle = angle if angle is not None else random.uniform(0, 360)
        speed = speed if speed is not None else random.uniform(0.6, 1.8)
        vx, vy = angle_to_vec(angle)
        self.vx = vx * speed
        self.vy = vy * speed
        self.rot      = random.uniform(0, 360)
        self.rot_spd  = random.uniform(-1.5, 1.5)
        self.shape    = random.choice(ASTEROID_SHAPES)
        self.alive    = True
        self.glow     = random.randint(0, 60)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.rot += self.rot_spd
        self.x, self.y = wrap(self.x, self.y)
        self.glow = (self.glow + 1) % 120

    def draw(self, surf):
        pts = poly_points(self.x, self.y, self.rot,
                          [(px * self.radius, py * self.radius) for px, py in self.shape])
        glow_alpha = int(40 + 30 * math.sin(math.radians(self.glow * 3)))
        col = tuple(min(255, c + glow_alpha // 4) for c in self.color)
        pygame.draw.polygon(surf, col, pts, 2)
        # inner shading
        inner = poly_points(self.x, self.y, self.rot,
                            [(px * self.radius * 0.6, py * self.radius * 0.6) for px, py in self.shape])
        pygame.draw.polygon(surf, (30, 30, 40), inner, 1)

    def children(self):
        next_size = {'large': 'medium', 'medium': 'small', 'small': None}[self.size_name]
        if not next_size:
            return []
        kids = []
        for _ in range(2):
            a = random.uniform(0, 360)
            s = random.uniform(1.0, 2.5)
            kids.append(Asteroid(self.x, self.y, next_size, a, s))
        return kids

# ── UFO ────────────────────────────────────────────────────────────────────────
class UFO:
    def __init__(self, level):
        side = random.choice([-1, 1])
        self.x  = 0 if side < 0 else WIDTH
        self.y  = random.uniform(100, HEIGHT - 100)
        self.vx = random.uniform(1.5, 2.5) * side
        self.vy = 0.0
        self.alive   = True
        self.radius  = 22
        self.shoot_cd = 0
        self.shoot_interval = max(60, 120 - level * 10)
        self.change_cd = 0
        self.accurate  = level >= 4

    def update(self, px, py):
        self.x += self.vx
        self.y += self.vy
        self.x, self.y = wrap(self.x, self.y)
        self.shoot_cd  -= 1
        self.change_cd -= 1
        if self.change_cd <= 0:
            self.vy = random.uniform(-1.5, 1.5)
            self.change_cd = random.randint(40, 90)

    def maybe_shoot(self, px, py):
        if self.shoot_cd > 0:
            return None
        self.shoot_cd = self.shoot_interval
        if self.accurate:
            dx, dy = px - self.x, py - self.y
            angle  = -math.degrees(math.atan2(dy, dx))
            angle += random.uniform(-15, 15)
        else:
            angle = random.uniform(0, 360)
        return Bullet(self.x, self.y, angle)

    def draw(self, surf, tick):
        cx, cy = int(self.x), int(self.y)
        flash = (tick // 8) % 2
        col   = YELLOW if flash else ORANGE
        # body
        pygame.draw.ellipse(surf, col,        (cx-22, cy-8,  44, 16), 2)
        pygame.draw.ellipse(surf, (50,50,20), (cx-22, cy-8,  44, 16))
        # dome
        pygame.draw.ellipse(surf, CYAN,       (cx-11, cy-18, 22, 18), 2)
        pygame.draw.ellipse(surf, (0,40,60),  (cx-11, cy-18, 22, 18))
        # lights
        for i, lx in enumerate(range(cx-16, cx+18, 8)):
            lc = YELLOW if (tick // 6 + i) % 3 != 0 else RED
            pygame.draw.circle(surf, lc, (lx, cy - 1), 3)

# ── Player Ship ────────────────────────────────────────────────────────────────
SHIP_SHAPE = [(0, -18), (-11, 12), (0, 7), (11, 12)]
THRUSTER   = [(0, 7), (-6, 12), (0, 20), (6, 12)]

class Ship:
    ROTATE_SPD = 4.0
    THRUST     = 0.22
    FRICTION   = 0.985
    MAX_SPEED  = 7.0
    SHOOT_CD   = 18

    def __init__(self):
        self.x = WIDTH  // 2
        self.y = HEIGHT // 2
        self.angle = 90.0
        self.vx = self.vy = 0.0
        self.alive      = True
        self.inv_timer  = 180
        self.shoot_timer= 0
        self.thrusting  = False
        self.thruster_frame = 0

    def update(self, keys, snd_thrust):
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.angle += self.ROTATE_SPD
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.angle -= self.ROTATE_SPD

        self.thrusting = keys[pygame.K_UP] or keys[pygame.K_w]
        if self.thrusting:
            vx, vy = angle_to_vec(self.angle)
            self.vx += vx * self.THRUST
            self.vy += vy * self.THRUST
            speed = math.hypot(self.vx, self.vy)
            if speed > self.MAX_SPEED:
                self.vx = self.vx / speed * self.MAX_SPEED
                self.vy = self.vy / speed * self.MAX_SPEED
            if random.random() < 0.4:
                snd_thrust.play()
            self.thruster_frame = (self.thruster_frame + 1) % 6
        else:
            self.thruster_frame = 0

        self.vx *= self.FRICTION
        self.vy *= self.FRICTION
        self.x  += self.vx
        self.y  += self.vy
        self.x, self.y = wrap(self.x, self.y)

        if self.inv_timer  > 0: self.inv_timer  -= 1
        if self.shoot_timer > 0: self.shoot_timer -= 1

    def shoot(self):
        if self.shoot_timer == 0:
            self.shoot_timer = self.SHOOT_CD
            return Bullet(self.x, self.y, self.angle)
        return None

    def draw(self, surf, tick):
        if not self.alive:
            return
        if self.inv_timer > 0 and (self.inv_timer // 5) % 2 == 0:
            return
        pts = poly_points(self.x, self.y, self.angle, SHIP_SHAPE)
        pygame.draw.polygon(surf, CYAN, pts, 2)
        # cockpit glow
        cp = poly_points(self.x, self.y, self.angle, [(0,-8),(-3,2),(0,0),(3,2)])
        try:
            pygame.draw.polygon(surf, (0, 60, 100), cp)
        except Exception:
            pass

        if self.thrusting and self.thruster_frame < 4:
            tf_pts = poly_points(self.x, self.y, self.angle, THRUSTER)
            flicker = random.choice([ORANGE, YELLOW, RED])
            pygame.draw.polygon(surf, flicker, tf_pts, 2)

    def thruster_particles(self):
        if not self.thrusting:
            return []
        vx, vy = angle_to_vec(self.angle)
        bx = self.x - vx * 12
        by = self.y - vy * 12
        parts = []
        for _ in range(3):
            a = self.angle + 180 + random.uniform(-25, 25)
            s = random.uniform(1, 3.5)
            avx, avy = angle_to_vec(a)
            life = random.randint(10, 22)
            color = random.choice([ORANGE, YELLOW, RED, WHITE])
            parts.append(Particle(bx, by, avx*s, avy*s, life, color, 2))
        return parts

# ── Starfield ──────────────────────────────────────────────────────────────────
class Starfield:
    def __init__(self, n=100):
        self.stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT),
                       random.randint(1, 3), random.randint(120, 220)) for _ in range(n)]

    def draw(self, surf, tick):
        for (x, y, sz, br) in self.stars:
            b = br + int(30 * math.sin(math.radians(tick * 2 + x)))
            b = max(80, min(255, b))
            pygame.draw.rect(surf, (b, b, b), (x, y, sz, sz))

# ── HUD helpers ────────────────────────────────────────────────────────────────
def draw_ship_icon(surf, cx, cy):
    pts = [(cx, cy-10), (cx-7, cy+7), (cx, cy+3), (cx+7, cy+7)]
    pygame.draw.polygon(surf, CYAN, pts, 2)

# ── Game ───────────────────────────────────────────────────────────────────────
class Game:
    MAX_LIVES       = 5
    EXTRA_LIFE_PTS  = 10000
    UFO_INTERVAL    = 1800   # frames

    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=RATE, size=-16, channels=2, buffer=512)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Asteroids")
        self.clock  = pygame.time.Clock()

        self.font_lg = pygame.font.SysFont("Courier", 40, bold=True)
        self.font_md = pygame.font.SysFont("Courier", 24, bold=True)
        self.font_sm = pygame.font.SysFont("Courier", 16)

        # Sounds
        try:
            self.snd_shoot     = make_shoot_snd()
            self.snd_explode_l = make_explode_snd(0.40, 60)
            self.snd_explode_m = make_explode_snd(0.25, 100)
            self.snd_explode_s = make_explode_snd(0.15, 180)
            self.snd_player    = make_explode_snd(0.50, 80)
            self.snd_thrust    = make_thrust_snd()
            self.snd_beat1     = make_beat_snd(120)
            self.snd_beat2     = make_beat_snd(100)
            self.snd_extra     = make_extra_life_snd()
        except Exception:
            class _S:
                def play(self): pass
            dummy = _S()
            for attr in ['snd_shoot','snd_explode_l','snd_explode_m','snd_explode_s',
                         'snd_player','snd_thrust','snd_beat1','snd_beat2','snd_extra']:
                setattr(self, attr, dummy)

        self.stars   = Starfield()
        self.hi      = 0
        self.state   = 'title'
        self.tick    = 0
        self.new_game()

    def new_game(self):
        self.score      = 0
        self.lives      = 3
        self.level      = 1
        self.next_extra = self.EXTRA_LIFE_PTS
        self.ship       = Ship()
        self.bullets: list[Bullet]   = []
        self.e_bullets: list[Bullet] = []
        self.asteroids: list[Asteroid] = []
        self.particles: list[Particle] = []
        self.ufo        = None
        self.ufo_timer  = self.UFO_INTERVAL
        self.beat_timer = 0
        self.beat_step  = 0
        self.beat_interval = 80
        self._spawn_asteroids(self.level + 3)
        self.state = 'playing'

    def _spawn_asteroids(self, n):
        for _ in range(n):
            while True:
                x = random.uniform(0, WIDTH)
                y = random.uniform(0, HEIGHT)
                if dist(x, y, self.ship.x, self.ship.y) > 120:
                    break
            self.asteroids.append(Asteroid(x, y, 'large'))

    def _next_level(self):
        self.level += 1
        self.bullets.clear()
        self.e_bullets.clear()
        self.ufo = None
        self.ufo_timer = self.UFO_INTERVAL
        self.beat_interval = max(20, 80 - self.level * 5)
        self._spawn_asteroids(min(self.level + 3, 12))

    def _respawn_ship(self):
        self.ship = Ship()
        self.ship.x = WIDTH  // 2
        self.ship.y = HEIGHT // 2
        self.bullets.clear()

    def _add_score(self, pts):
        self.score += pts
        self.hi     = max(self.hi, self.score)
        if self.score >= self.next_extra:
            self.lives = min(self.lives + 1, self.MAX_LIVES)
            self.next_extra += self.EXTRA_LIFE_PTS
            self.snd_extra.play()
            self.particles += explode(self.ship.x, self.ship.y, 15, GREEN, 2)

    # ── Update ─────────────────────────────────────────────────────────────────
    def update(self):
        self.tick += 1
        if self.state != 'playing':
            return

        keys = pygame.key.get_pressed()

        # Ship
        if self.ship.alive:
            self.ship.update(keys, self.snd_thrust)
            self.particles += self.ship.thruster_particles()

            if keys[pygame.K_SPACE] or keys[pygame.K_LCTRL]:
                b = self.ship.shoot()
                if b:
                    self.bullets.append(b)
                    self.snd_shoot.play()

        # Bullets
        for b in self.bullets + self.e_bullets:
            b.update()
        self.bullets   = [b for b in self.bullets   if b.alive]
        self.e_bullets = [b for b in self.e_bullets if b.alive]

        # Asteroids
        for a in self.asteroids:
            a.update()

        # UFO
        self.ufo_timer -= 1
        if self.ufo is None and self.ufo_timer <= 0 and self.asteroids:
            self.ufo = UFO(self.level)
            self.ufo_timer = self.UFO_INTERVAL + random.randint(-300, 300)

        if self.ufo:
            self.ufo.update(self.ship.x, self.ship.y)
            eb = self.ufo.maybe_shoot(self.ship.x, self.ship.y)
            if eb:
                self.e_bullets.append(eb)
            if not (0 <= self.ufo.x <= WIDTH):
                self.ufo = None

        # Particles
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        # Beat
        self.beat_timer -= 1
        if self.beat_timer <= 0:
            self.beat_timer = self.beat_interval
            (self.snd_beat1 if self.beat_step % 2 == 0 else self.snd_beat2).play()
            self.beat_step += 1

        # ── Collisions ─────────────────────────────────────────────────────────

        # Player bullets vs asteroids
        new_rocks = []
        for b in list(self.bullets):
            for a in list(self.asteroids):
                if b.alive and a.alive and dist(b.x, b.y, a.x, a.y) < a.radius:
                    b.alive = False
                    a.alive = False
                    self._add_score(a.pts)
                    new_rocks  += a.children()
                    snd = {'large': self.snd_explode_l,
                           'medium': self.snd_explode_m,
                           'small': self.snd_explode_s}[a.size_name]
                    snd.play()
                    self.particles += explode(a.x, a.y, 16, ORANGE, a.radius * 0.07)
        self.asteroids = [a for a in self.asteroids if a.alive] + new_rocks
        self.bullets   = [b for b in self.bullets   if b.alive]

        # Player bullets vs UFO
        if self.ufo:
            for b in list(self.bullets):
                if b.alive and dist(b.x, b.y, self.ufo.x, self.ufo.y) < self.ufo.radius:
                    b.alive = False
                    self._add_score(500 if self.ufo.accurate else 200)
                    self.particles += explode(self.ufo.x, self.ufo.y, 25, YELLOW, 3)
                    self.snd_explode_l.play()
                    self.ufo = None
                    break
            self.bullets = [b for b in self.bullets if b.alive]

        # Ship vs asteroids / UFO bullets / UFO
        if self.ship.alive and self.ship.inv_timer == 0:
            hit = False
            for a in self.asteroids:
                if dist(self.ship.x, self.ship.y, a.x, a.y) < a.radius * 0.85:
                    hit = True
                    break
            for eb in self.e_bullets:
                if eb.alive and dist(self.ship.x, self.ship.y, eb.x, eb.y) < 10:
                    hit = True
                    eb.alive = False
                    break
            if self.ufo and dist(self.ship.x, self.ship.y, self.ufo.x, self.ufo.y) < self.ufo.radius:
                hit = True
            if hit:
                self.snd_player.play()
                self.particles += explode(self.ship.x, self.ship.y, 40, CYAN, 4)
                self.lives -= 1
                self.ship.alive = False
                if self.lives > 0:
                    pygame.time.set_timer(pygame.USEREVENT, 2200)
                else:
                    self.hi    = max(self.hi, self.score)
                    pygame.time.set_timer(pygame.USEREVENT + 1, 2500)

        self.e_bullets = [b for b in self.e_bullets if b.alive]

        # Next level
        if not self.asteroids and self.ufo is None:
            self._next_level()

    # ── Draw ───────────────────────────────────────────────────────────────────
    def draw(self):
        self.screen.fill(BLACK)
        self.stars.draw(self.screen, self.tick)

        if self.state == 'title':
            self._draw_title()
            pygame.display.flip()
            return

        # Objects
        for p in self.particles:
            p.draw(self.screen)
        for a in self.asteroids:
            a.draw(self.screen)
        if self.ufo:
            self.ufo.draw(self.screen, self.tick)
        for b in self.bullets + self.e_bullets:
            b.draw(self.screen)
        self.ship.draw(self.screen, self.tick)

        # HUD
        score_txt = self.font_md.render(f"{self.score:07d}", True, WHITE)
        hi_txt    = self.font_md.render(f"HI {self.hi:07d}", True, YELLOW)
        lvl_txt   = self.font_sm.render(f"LEVEL {self.level}", True, CYAN)
        self.screen.blit(score_txt, (10, 10))
        self.screen.blit(hi_txt,    (WIDTH//2 - hi_txt.get_width()//2, 10))
        self.screen.blit(lvl_txt,   (WIDTH - lvl_txt.get_width() - 10, 10))

        # Lives icons
        for i in range(self.lives):
            draw_ship_icon(self.screen, 20 + i * 28, HEIGHT - 22)

        # Extra life threshold
        nxt = self.font_sm.render(f"+1UP @ {self.next_extra}", True, GREY)
        self.screen.blit(nxt, (WIDTH - nxt.get_width() - 10, HEIGHT - 24))

        if self.state == 'game_over':
            self._overlay("GAME OVER", RED, "R — New Game    Q — Quit")
        elif self.state == 'paused':
            self._overlay("PAUSED", YELLOW, "P — Resume")

        pygame.display.flip()

    def _overlay(self, title, color, sub):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        self.screen.blit(s, (0, 0))
        t = self.font_lg.render(title, True, color)
        self.screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 45))
        t2 = self.font_sm.render(sub, True, WHITE)
        self.screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 + 20))

    def _draw_title(self):
        t = self.font_lg.render("A S T E R O I D S", True, WHITE)
        self.screen.blit(t, (WIDTH//2 - t.get_width()//2, 160))

        lines = [
            ("← → / A D",   "Rotate"),
            ("↑ / W",        "Thrust"),
            ("SPACE / CTRL", "Fire"),
            ("P",            "Pause"),
            ("R",            "Restart"),
            ("Q",            "Quit"),
        ]
        for i, (key, act) in enumerate(lines):
            k = self.font_sm.render(key,  True, CYAN)
            a = self.font_sm.render(act,  True, WHITE)
            y = 280 + i * 30
            self.screen.blit(k, (WIDTH//2 - 160, y))
            self.screen.blit(a, (WIDTH//2 + 20,  y))

        blink = self.font_md.render("PRESS SPACE TO START", True, YELLOW)
        if (self.tick // 30) % 2 == 0:
            self.screen.blit(blink, (WIDTH//2 - blink.get_width()//2, 490))

        if self.hi > 0:
            hi = self.font_sm.render(f"HI-SCORE  {self.hi:07d}", True, ORANGE)
            self.screen.blit(hi, (WIDTH//2 - hi.get_width()//2, 550))

    # ── Events ─────────────────────────────────────────────────────────────────
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.USEREVENT:          # respawn ship
                pygame.time.set_timer(pygame.USEREVENT, 0)
                self._respawn_ship()

            if event.type == pygame.USEREVENT + 1:      # game over delay
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                self.state = 'game_over'

            if event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_q:
                    pygame.quit(); sys.exit()

                if self.state == 'title':
                    if k == pygame.K_SPACE:
                        self.new_game()

                elif self.state == 'playing':
                    if k == pygame.K_p:
                        self.state = 'paused'

                elif self.state == 'paused':
                    if k == pygame.K_p:
                        self.state = 'playing'

                elif self.state == 'game_over':
                    if k == pygame.K_r:
                        self.new_game()

                if k == pygame.K_r and self.state in ('game_over', 'playing'):
                    self.new_game()

    # ── Main loop ──────────────────────────────────────────────────────────────
    def run(self):
        while True:
            self.handle_events()
            if self.state == 'playing':
                self.update()
            else:
                self.tick += 1
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()
