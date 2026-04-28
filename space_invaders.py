"""
Space Invaders — Python + Pygame
Run: python space_invaders.py
Requires: pip install pygame
"""

import pygame
import random
import sys

# ── Constants ──────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 800, 650
FPS           = 60

# Colours
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
GREEN   = (0,   255, 80)
RED     = (255, 50,  50)
CYAN    = (0,   220, 255)
YELLOW  = (255, 230, 0)
MAGENTA = (220, 0,   220)
ORANGE  = (255, 140, 0)
GREY    = (80,  80,  80)
DKGREEN = (0,   140, 40)

# Invader rows → colour
ROW_COLORS = [MAGENTA, RED, ORANGE, YELLOW, GREEN]

# ── Helper: draw pixel-art sprites via coordinate lists ────────────────────────
def draw_sprite(surf, color, pixels, ox, oy, scale=3):
    for (px, py) in pixels:
        pygame.draw.rect(surf, color,
                         (ox + px * scale, oy + py * scale, scale, scale))

# ── Pixel-art templates (11×8 grid) ───────────────────────────────────────────
INVADER_A = [  # crab-style (rows 0-1)
    (1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,0),(9,0),
    (0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(10,1),
    (0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(10,2),
    (0,3),(1,3),(3,3),(4,3),(5,3),(6,3),(7,3),(9,3),(10,3),
    (0,4),(1,4),(2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(8,4),(9,4),(10,4),
    (1,5),(2,5),(4,5),(5,5),(6,5),(8,5),(9,5),
    (0,6),(1,6),(3,6),(4,6),(5,6),(6,6),(7,6),(9,6),(10,6),
    (0,7),(2,7),(8,7),(10,7),
]
INVADER_B = [  # squid-style (rows 2-3)
    (3,0),(4,0),(5,0),(6,0),(7,0),
    (2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),
    (1,2),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),
    (0,3),(1,3),(2,3),(4,3),(5,3),(6,3),(8,3),(9,3),(10,3),
    (0,4),(1,4),(2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(8,4),(9,4),(10,4),
    (1,5),(2,5),(4,5),(6,5),(8,5),(9,5),
    (2,6),(3,6),(7,6),(8,6),
    (1,7),(2,7),(8,7),(9,7),
]
INVADER_C = [  # helmet-style (row 4)
    (4,0),(5,0),(6,0),
    (2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),
    (1,2),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),
    (0,3),(1,3),(2,3),(4,3),(5,3),(6,3),(8,3),(9,3),(10,3),
    (0,4),(1,4),(2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(8,4),(9,4),(10,4),
    (0,5),(2,5),(3,5),(4,5),(5,5),(6,5),(7,5),(8,5),(10,5),
    (0,6),(1,6),(3,6),(7,6),(9,6),(10,6),
    (2,7),(3,7),(7,7),(8,7),
]

UFO_PIXELS = [
    (3,0),(4,0),(5,0),(6,0),(7,0),
    (1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),
    (0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(10,2),
    (1,3),(3,3),(5,3),(7,3),(9,3),
    (0,4),(1,4),(2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(8,4),(9,4),(10,4),
]

PLAYER_PIXELS = [
    (5,0),
    (4,1),(5,1),(6,1),
    (3,2),(4,2),(5,2),(6,2),(7,2),
    (2,3),(3,3),(4,3),(5,3),(6,3),(7,3),(8,3),
    (1,4),(2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(8,4),(9,4),
    (0,5),(1,5),(2,5),(3,5),(4,5),(5,5),(6,5),(7,5),(8,5),(9,5),(10,5),
    (0,6),(1,6),(2,6),(3,6),(4,6),(5,6),(6,6),(7,6),(8,6),(9,6),(10,6),
]

BARRIER_PIXELS = [
    (2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,0),
    (1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),
    (0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(10,2),
    (0,3),(1,3),(2,3),(3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(9,3),(10,3),
    (0,4),(1,4),(2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(8,4),(9,4),(10,4),
    (0,5),(1,5),(2,5),(7,5),(8,5),(9,5),(10,5),
    (0,6),(1,6),(2,6),(8,6),(9,6),(10,6),
]

SCALE_INV  = 3   # invader pixel scale
SCALE_PLR  = 3
SCALE_BAR  = 3

INV_W  = 11 * SCALE_INV
INV_H  = 8  * SCALE_INV
BAR_W  = 11 * SCALE_BAR
BAR_H  = 7  * SCALE_BAR

# ── Bullet ─────────────────────────────────────────────────────────────────────
class Bullet:
    def __init__(self, x, y, dy, color=WHITE):
        self.x = x
        self.y = y
        self.dy = dy          # positive = down, negative = up
        self.color = color
        self.alive = True
        self.w, self.h = 3, 12

    def update(self):
        self.y += self.dy
        if self.y < -20 or self.y > HEIGHT + 20:
            self.alive = False

    def draw(self, surf):
        pygame.draw.rect(surf, self.color,
                         (self.x - self.w//2, self.y, self.w, self.h))

    def rect(self):
        return pygame.Rect(self.x - self.w//2, self.y, self.w, self.h)

# ── Barrier ────────────────────────────────────────────────────────────────────
class Barrier:
    BLOCK = 4   # each pixel is 4×4 px

    # Build a set of alive pixel coords from the template
    def __init__(self, cx, y):
        self.ox = cx - (BAR_W // 2)
        self.oy = y
        self.pixels = set(BARRIER_PIXELS)   # (px, py) alive

    def draw(self, surf):
        for (px, py) in self.pixels:
            pygame.draw.rect(surf, DKGREEN,
                (self.ox + px * SCALE_BAR,
                 self.oy + py * SCALE_BAR,
                 SCALE_BAR, SCALE_BAR))

    def check_bullet(self, bullet):
        """Damage barrier, return True if bullet should die."""
        br = bullet.rect()
        for (px, py) in list(self.pixels):
            r = pygame.Rect(self.ox + px * SCALE_BAR,
                            self.oy + py * SCALE_BAR,
                            SCALE_BAR, SCALE_BAR)
            if br.colliderect(r):
                self.pixels.discard((px, py))
                # remove neighbours too for crater effect
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
                    if random.random() < 0.5:
                        self.pixels.discard((px+dx, py+dy))
                return True
        return False

# ── Invader ────────────────────────────────────────────────────────────────────
class Invader:
    TEMPLATES = [INVADER_A, INVADER_A,
                 INVADER_B, INVADER_B,
                 INVADER_C]

    def __init__(self, col, row, x, y):
        self.col  = col
        self.row  = row
        self.x    = x
        self.y    = y
        self.alive = True
        self.frame = 0
        self.template = self.TEMPLATES[row % len(self.TEMPLATES)]
        self.color = ROW_COLORS[row % len(ROW_COLORS)]
        self.death_timer = 0   # frames of explosion to show

    def draw(self, surf):
        if not self.alive:
            if self.death_timer > 0:
                # draw X explosion
                cx = self.x + INV_W // 2
                cy = self.y + INV_H // 2
                r  = 10
                for dx, dy in [(-r,-r),(r,-r),(-r,r),(r,r),(0,-r),(0,r),(-r,0),(r,0)]:
                    pygame.draw.line(surf, RED,
                                     (cx, cy), (cx+dx//2, cy+dy//2), 2)
            return
        draw_sprite(surf, self.color, self.template,
                    self.x, self.y, SCALE_INV)

    def rect(self):
        return pygame.Rect(self.x, self.y, INV_W, INV_H)

# ── UFO ────────────────────────────────────────────────────────────────────────
class UFO:
    SCORE = [50, 100, 150, 300]

    def __init__(self):
        self.reset()

    def reset(self):
        self.active = False
        self.x = -80
        self.y = 55
        self.dx = 2
        self.score_val = random.choice(self.SCORE)
        self.flash_timer = 0  # show score text briefly after hit

    def spawn(self):
        self.active = True
        self.x = -80
        self.dx = 2

    def update(self):
        if not self.active:
            return
        if self.flash_timer > 0:
            self.flash_timer -= 1
            if self.flash_timer == 0:
                self.active = False
            return
        self.x += self.dx
        if self.x > WIDTH + 20:
            self.active = False

    def draw(self, surf, font_sm):
        if not self.active:
            return
        if self.flash_timer > 0:
            txt = font_sm.render(str(self.score_val), True, RED)
            surf.blit(txt, (self.x, self.y))
            return
        draw_sprite(surf, RED, UFO_PIXELS, int(self.x), self.y, SCALE_INV)

    def rect(self):
        return pygame.Rect(int(self.x), self.y, INV_W, 5 * SCALE_INV)

# ── Player ─────────────────────────────────────────────────────────────────────
class Player:
    SPEED      = 4
    SHOOT_CD   = 35   # frames between shots

    def __init__(self):
        self.x  = WIDTH // 2 - (11 * SCALE_PLR) // 2
        self.y  = HEIGHT - 80
        self.hp = 3
        self.shoot_timer = 0
        self.inv_timer   = 0   # invincibility after hit
        self.alive       = True

    def update(self, keys):
        if not self.alive:
            return
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            self.x = max(0, self.x - self.SPEED)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x = min(WIDTH - 11 * SCALE_PLR, self.x + self.SPEED)
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
        if self.inv_timer > 0:
            self.inv_timer -= 1

    def shoot(self):
        if self.shoot_timer == 0:
            self.shoot_timer = self.SHOOT_CD
            cx = self.x + (11 * SCALE_PLR) // 2
            return Bullet(cx, self.y - 12, -9, CYAN)
        return None

    def hit(self):
        if self.inv_timer > 0:
            return
        self.hp -= 1
        self.inv_timer = 90
        if self.hp <= 0:
            self.alive = False

    def draw(self, surf):
        if not self.alive:
            return
        # blink while invincible
        if self.inv_timer > 0 and (self.inv_timer // 6) % 2 == 0:
            return
        color = CYAN if self.alive else RED
        draw_sprite(surf, color, PLAYER_PIXELS, self.x, self.y, SCALE_PLR)

    def rect(self):
        return pygame.Rect(self.x, self.y, 11 * SCALE_PLR, 7 * SCALE_PLR)

# ── Grid of invaders ───────────────────────────────────────────────────────────
class InvaderGrid:
    COLS = 11
    ROWS = 5
    X_GAP = 16   # extra spacing between invaders
    Y_GAP = 8

    def __init__(self, level=1):
        self.level  = level
        self.base_speed   = 0.4 + (level - 1) * 0.15
        self.dx     = self.base_speed
        self.dy     = 18            # drop amount per edge hit
        self.move_cd      = max(6, 50 - level * 4)
        self.move_timer   = self.move_cd
        self.anim_frame   = 0
        self.invaders: list[Invader] = []
        self._build()

    def _build(self):
        self.invaders.clear()
        start_x = 60
        start_y = 100
        for row in range(self.ROWS):
            for col in range(self.COLS):
                x = start_x + col * (INV_W + self.X_GAP)
                y = start_y + row * (INV_H + self.Y_GAP)
                self.invaders.append(Invader(col, row, x, y))

    def alive_list(self):
        return [inv for inv in self.invaders if inv.alive]

    def update(self):
        # tick death explosions
        for inv in self.invaders:
            if not inv.alive and inv.death_timer > 0:
                inv.death_timer -= 1

        alive = self.alive_list()
        if not alive:
            return

        self.move_timer -= 1
        if self.move_timer > 0:
            return
        alive_count = len(alive)
        speed_boost  = max(0.5, (self.COLS * self.ROWS - alive_count) / (self.COLS * self.ROWS))
        self.move_cd = max(3, int((50 - self.level * 4) * (1 - speed_boost * 0.7)))
        self.move_timer = self.move_cd
        self.anim_frame = 1 - self.anim_frame

        # check edges
        xs = [inv.x for inv in alive]
        hit_right = (self.dx > 0 and max(xs) + INV_W >= WIDTH - 10)
        hit_left  = (self.dx < 0 and min(xs) <= 10)

        if hit_right or hit_left:
            self.dx = -self.dx
            for inv in alive:
                inv.y += self.dy
        else:
            for inv in alive:
                inv.x += self.dx

    def lowest_in_column(self):
        """Return the lowest alive invader per column (for shooting)."""
        cols: dict[int, Invader] = {}
        for inv in self.alive_list():
            if inv.col not in cols or inv.y > cols[inv.col].y:
                cols[inv.col] = inv
        return list(cols.values())

    def invaders_reached_bottom(self):
        alive = self.alive_list()
        if not alive:
            return False
        return max(inv.y + INV_H for inv in alive) >= HEIGHT - 120

    def draw(self, surf):
        for inv in self.invaders:
            inv.draw(surf)

# ── Stars ──────────────────────────────────────────────────────────────────────
class Starfield:
    def __init__(self, n=80):
        self.stars = [(random.randint(0, WIDTH),
                       random.randint(0, HEIGHT),
                       random.randint(1, 3)) for _ in range(n)]

    def draw(self, surf, tick):
        for (x, y, s) in self.stars:
            bright = 150 + int(50 * ((tick // 30 + x) % 2))
            c = (bright, bright, bright)
            pygame.draw.rect(surf, c, (x, y, s, s))

# ── Main Game ──────────────────────────────────────────────────────────────────
class Game:
    UFO_INTERVAL = 900   # frames between UFO spawns

    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock  = pygame.time.Clock()

        self.font_lg = pygame.font.SysFont("Courier", 36, bold=True)
        self.font_md = pygame.font.SysFont("Courier", 22, bold=True)
        self.font_sm = pygame.font.SysFont("Courier", 16)

        self._make_sounds()
        self.reset()

    # ── Sound generation (no external files needed) ────────────────────────────
    def _make_sounds(self):
        import numpy as np
        rate = 22050

        def make_sound(freq, dur, vol=0.4, wave='square', decay=1.0):
            frames = int(rate * dur)
            t = np.linspace(0, dur, frames, endpoint=False)
            if wave == 'square':
                s = np.sign(np.sin(2 * np.pi * freq * t))
            elif wave == 'sine':
                s = np.sin(2 * np.pi * freq * t)
            else:
                s = (2 * (t * freq % 1) - 1)   # sawtooth
            env = np.exp(-decay * t / dur * frames / frames * 5) if decay else 1
            env = np.linspace(1, 0, frames) ** 0.5
            s = (s * env * vol * 32767).astype(np.int16)
            stereo = np.column_stack([s, s])
            return pygame.sndarray.make_sound(stereo)

        try:
            self.snd_shoot   = make_sound(880,  0.10, wave='square')
            self.snd_explode = make_sound(120,  0.25, wave='sawtooth')
            self.snd_ufo     = make_sound(440,  0.15, wave='sine')
            self.snd_march   = [make_sound(f, 0.05, wave='square')
                                for f in [160, 180, 200, 180]]
        except Exception:
            class _Snd:
                def play(self): pass
            dummy = _Snd()
            self.snd_shoot = self.snd_explode = self.snd_ufo = dummy
            self.snd_march = [dummy] * 4

        self.march_idx   = 0
        self.march_timer = 0

    def reset(self, level=1):
        self.level    = level
        self.score    = 0 if level == 1 else self.score
        self.hi_score = getattr(self, 'hi_score', 0)
        self.player   = Player()
        self.grid     = InvaderGrid(level)
        self.barriers = [Barrier(cx, HEIGHT - 115)
                         for cx in [140, 280, 420, 560, 700]]
        self.p_bullets: list[Bullet] = []
        self.e_bullets: list[Bullet] = []
        self.ufo      = UFO()
        self.ufo_timer = self.UFO_INTERVAL
        self.stars    = Starfield()
        self.tick     = 0
        self.state    = 'playing'   # 'playing' | 'game_over' | 'win'
        self.pause    = False

    # ── Shooting helpers ───────────────────────────────────────────────────────
    def _enemy_shoot(self):
        shooters = self.grid.lowest_in_column()
        if not shooters:
            return
        inv = random.choice(shooters)
        cx  = inv.x + INV_W // 2
        self.e_bullets.append(Bullet(cx, inv.y + INV_H, 4 + self.level * 0.3, RED))

    # ── Update ─────────────────────────────────────────────────────────────────
    def update(self):
        if self.pause or self.state != 'playing':
            return
        self.tick += 1
        keys = pygame.key.get_pressed()

        # Player
        self.player.update(keys)
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
            b = self.player.shoot()
            if b:
                self.p_bullets.append(b)
                self.snd_shoot.play()

        # March sound
        if self.grid.alive_list():
            self.march_timer -= 1
            if self.march_timer <= 0:
                self.march_timer = max(4, self.grid.move_cd)
                self.snd_march[self.march_idx % 4].play()
                self.march_idx += 1

        # Invader grid
        self.grid.update()

        # UFO
        self.ufo_timer -= 1
        if self.ufo_timer <= 0 and not self.ufo.active:
            self.ufo.spawn()
            self.ufo_timer = self.UFO_INTERVAL + random.randint(-200, 200)
        self.ufo.update()

        # Enemy shooting
        if self.tick % max(30, 70 - self.level * 5) == 0:
            self._enemy_shoot()

        # Bullet movement
        for b in self.p_bullets + self.e_bullets:
            b.update()
        self.p_bullets = [b for b in self.p_bullets if b.alive]
        self.e_bullets = [b for b in self.e_bullets if b.alive]

        # ── Collision: player bullets vs invaders ──────────────────────────────
        for b in list(self.p_bullets):
            for inv in self.grid.invaders:
                if inv.alive and b.alive and b.rect().colliderect(inv.rect()):
                    inv.alive = False
                    inv.death_timer = 12
                    b.alive = False
                    pts = [30,20,20,10,10]
                    self.score += pts[inv.row % len(pts)]
                    self.snd_explode.play()
                    break

        # ── Collision: player bullets vs UFO ──────────────────────────────────
        for b in list(self.p_bullets):
            if (b.alive and self.ufo.active and
                    self.ufo.flash_timer == 0 and
                    b.rect().colliderect(self.ufo.rect())):
                b.alive = False
                self.score += self.ufo.score_val
                self.ufo.flash_timer = 80
                self.snd_explode.play()

        # ── Collision: enemy bullets vs barriers ──────────────────────────────
        for b in list(self.e_bullets):
            for bar in self.barriers:
                if b.alive and bar.check_bullet(b):
                    b.alive = False
                    break

        # ── Collision: player bullets vs barriers ─────────────────────────────
        for b in list(self.p_bullets):
            for bar in self.barriers:
                if b.alive and bar.check_bullet(b):
                    b.alive = False
                    break

        # ── Collision: enemy bullets vs player ────────────────────────────────
        for b in list(self.e_bullets):
            if b.alive and b.rect().colliderect(self.player.rect()):
                self.player.hit()
                b.alive = False
                self.snd_explode.play()

        # Clean dead bullets
        self.p_bullets = [b for b in self.p_bullets if b.alive]
        self.e_bullets = [b for b in self.e_bullets if b.alive]

        # ── Win / Lose checks ─────────────────────────────────────────────────
        if not self.grid.alive_list():
            self.hi_score = max(self.hi_score, self.score)
            self.state = 'win'
        if not self.player.alive or self.grid.invaders_reached_bottom():
            self.hi_score = max(self.hi_score, self.score)
            self.state = 'game_over'

    # ── Draw ───────────────────────────────────────────────────────────────────
    def draw(self):
        self.screen.fill(BLACK)
        self.stars.draw(self.screen, self.tick)

        # HUD
        score_txt = self.font_md.render(f"SCORE  {self.score:05d}", True, WHITE)
        hi_txt    = self.font_md.render(f"HI  {self.hi_score:05d}",   True, YELLOW)
        lvl_txt   = self.font_md.render(f"LVL {self.level}",           True, CYAN)
        self.screen.blit(score_txt, (10, 10))
        self.screen.blit(hi_txt,    (WIDTH//2 - hi_txt.get_width()//2, 10))
        self.screen.blit(lvl_txt,   (WIDTH - lvl_txt.get_width() - 10, 10))

        # Lives
        for i in range(self.player.hp):
            draw_sprite(self.screen, CYAN, PLAYER_PIXELS,
                        10 + i * (11 * SCALE_PLR + 6), HEIGHT - 30, SCALE_PLR)

        # Ground line
        pygame.draw.line(self.screen, GREEN, (0, HEIGHT - 35), (WIDTH, HEIGHT - 35), 2)

        # Game objects
        for bar in self.barriers:
            bar.draw(self.screen)
        self.grid.draw(self.screen)
        self.ufo.draw(self.screen, self.font_sm)
        self.player.draw(self.screen)
        for b in self.p_bullets + self.e_bullets:
            b.draw(self.screen)

        # Overlays
        if self.state == 'game_over':
            self._overlay("GAME OVER", RED,
                          "Press R to restart  |  Q to quit")
        elif self.state == 'win':
            self._overlay("YOU WIN!", GREEN,
                          f"Next Level in 3s…  |  R to restart  |  Q to quit")

        if self.pause and self.state == 'playing':
            self._overlay("PAUSED", YELLOW, "Press P to continue")

        pygame.display.flip()

    def _overlay(self, title, color, sub):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 160))
        self.screen.blit(s, (0, 0))
        t = self.font_lg.render(title, True, color)
        self.screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 40))
        t2 = self.font_sm.render(sub, True, WHITE)
        self.screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 + 20))

    # ── Event handling ─────────────────────────────────────────────────────────
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_r:
                    self.score = 0
                    self.reset(1)
                if event.key == pygame.K_p and self.state == 'playing':
                    self.pause = not self.pause

        # Auto-advance to next level after win
        if self.state == 'win':
            if not hasattr(self, '_win_tick'):
                self._win_tick = self.tick
            if self.tick - self._win_tick > FPS * 3:
                del self._win_tick
                self.reset(self.level + 1)

    # ── Main loop ──────────────────────────────────────────────────────────────
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

# ── Title screen ───────────────────────────────────────────────────────────────
def title_screen(screen, font_lg, font_md, font_sm, stars, clock):
    tick = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()

        screen.fill(BLACK)
        stars.draw(screen, tick)

        title = font_lg.render("SPACE  INVADERS", True, GREEN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))

        # Draw demo invaders
        demo = [(INVADER_A, MAGENTA), (INVADER_B, YELLOW), (INVADER_C, CYAN)]
        for i, (tmpl, col) in enumerate(demo):
            draw_sprite(screen, col, tmpl, WIDTH//2 - 80, 230 + i * 50, SCALE_INV)
            pts = ["= 30 PTS", "= 20 PTS", "= 10 PTS"][i]
            txt = font_sm.render(pts, True, WHITE)
            screen.blit(txt, (WIDTH//2 - 20, 235 + i * 50))

        draw_sprite(screen, RED, UFO_PIXELS, WIDTH//2 - 80, 390, SCALE_INV)
        txt = font_sm.render("= ??? PTS", True, WHITE)
        screen.blit(txt, (WIDTH//2 - 20, 395))

        blink = font_md.render("PRESS SPACE TO PLAY", True, WHITE)
        if (tick // 30) % 2 == 0:
            screen.blit(blink, (WIDTH//2 - blink.get_width()//2, 470))

        ctrl = font_sm.render("← → / A D : Move    SPACE / W : Shoot    P : Pause", True, GREY)
        screen.blit(ctrl, (WIDTH//2 - ctrl.get_width()//2, 540))

        pygame.display.flip()
        clock.tick(FPS)
        tick += 1

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Invaders")
    clock  = pygame.time.Clock()
    font_lg = pygame.font.SysFont("Courier", 36, bold=True)
    font_md = pygame.font.SysFont("Courier", 22, bold=True)
    font_sm = pygame.font.SysFont("Courier", 16)
    stars   = Starfield()

    title_screen(screen, font_lg, font_md, font_sm, stars, clock)
    Game().run()
